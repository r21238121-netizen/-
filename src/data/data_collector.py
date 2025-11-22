"""
Data Collection Module for BingX Futures
Collects OHLCV data via REST API and stores locally
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
import sqlite3
import pyarrow.parquet as pq
import pyarrow as pa
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import os
from pathlib import Path

class DataCollector:
    def __init__(self, config_path: Optional[str] = None):
        self.base_url = "https://open-api.bingx.com"
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'pairs': ['BTC-USDT'],
            'timeframes': ['1m', '5m', '15m', '1h'],
            'db_path': './data/trading_data.db',
            'parquet_path': './data/parquet/',
            'data_limit': 1000  # per request
        }
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            import json
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        # Create directories
        os.makedirs(os.path.dirname(self.config['db_path']), exist_ok=True)
        os.makedirs(self.config['parquet_path'], exist_ok=True)
        
        # Initialize database
        self.init_db()

    def init_db(self):
        """Initialize SQLite database for storing logs and metadata"""
        conn = sqlite3.connect(self.config['db_path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_time INTEGER,
                end_time INTEGER,
                record_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    async def create_session(self):
        """Create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_klines(self, pair: str, timeframe: str, start_time: int, 
                          end_time: int = None, limit: int = 1000) -> List[Dict]:
        """Fetch klines data from BingX API"""
        await self.create_session()
        
        url = f"{self.base_url}/openApi/quote/v1/klines"
        params = {
            'symbol': pair.replace('-', ''),
            'interval': timeframe,
            'startTime': start_time,
            'limit': min(limit, 1000)  # API limit
        }
        
        if end_time:
            params['endTime'] = end_time
            
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        # Convert API response to structured format
                        klines = []
                        for item in data['data']:
                            kline = {
                                'timestamp': int(item[0]),
                                'open': float(item[1]),
                                'high': float(item[2]),
                                'low': float(item[3]),
                                'close': float(item[4]),
                                'volume': float(item[5]),
                                'close_time': int(item[6]),
                                'quote_asset_volume': float(item[7]),
                                'number_of_trades': int(item[8]),
                                'taker_buy_base_asset_volume': float(item[9]),
                                'taker_buy_quote_asset_volume': float(item[10])
                            }
                            klines.append(kline)
                        return klines
                    else:
                        self.logger.error(f"No data in response: {data}")
                        return []
                else:
                    self.logger.error(f"Error fetching klines: {response.status}")
                    error_text = await response.text()
                    self.logger.error(f"Error details: {error_text}")
                    return []
        except Exception as e:
            self.logger.error(f"Exception in fetch_klines: {e}")
            return []

    def save_to_parquet(self, df: pd.DataFrame, pair: str, timeframe: str):
        """Save DataFrame to Parquet file"""
        filename = f"{self.config['parquet_path']}/{pair}_{timeframe}.parquet"
        table = pa.Table.from_pandas(df)
        pq.write_table(table, filename)
        self.logger.info(f"Saved {len(df)} records to {filename}")

    def save_to_db(self, pair: str, timeframe: str, start_time: int, 
                   end_time: int, record_count: int):
        """Save collection log to database"""
        conn = sqlite3.connect(self.config['db_path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_logs (pair, timeframe, start_time, end_time, record_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (pair, timeframe, start_time, end_time, record_count))
        
        conn.commit()
        conn.close()

    async def collect_data(self, pair: str, timeframe: str, days_back: int = 365):
        """Collect historical data for a specific pair and timeframe"""
        self.logger.info(f"Collecting data for {pair} {timeframe}, {days_back} days back")
        
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
        
        all_klines = []
        current_start = start_time
        
        # Determine step based on timeframe
        timeframe_seconds = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000
        }
        
        step = timeframe_seconds.get(timeframe, 60 * 1000) * 1000  # 1000 klines per request
        
        while current_start < end_time:
            # Calculate end time for this batch
            batch_end = min(current_start + step, end_time)
            
            klines = await self.fetch_klines(pair, timeframe, current_start, batch_end)
            
            if klines:
                all_klines.extend(klines)
                self.logger.info(f"Fetched {len(klines)} klines from {current_start} to {batch_end}")
                
                # Update start time for next batch
                # Use the close_time of the last kline to avoid duplicates
                if klines:
                    current_start = klines[-1]['close_time'] + 1
                else:
                    current_start = batch_end
            else:
                # If no data returned, move forward by step to avoid infinite loop
                current_start = batch_end
            
            # Add small delay to respect API limits
            await asyncio.sleep(0.2)
        
        if all_klines:
            # Convert to DataFrame
            df = pd.DataFrame(all_klines)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Save to Parquet
            self.save_to_parquet(df, pair, timeframe)
            
            # Save log to DB
            self.save_to_db(pair, timeframe, start_time, end_time, len(df))
            
            self.logger.info(f"Completed collection for {pair} {timeframe}: {len(df)} records")
            
            return df
        else:
            self.logger.warning(f"No data collected for {pair} {timeframe}")
            return pd.DataFrame()

    async def collect_all_data(self, days_back: int = 365):
        """Collect data for all configured pairs and timeframes"""
        for pair in self.config['pairs']:
            for timeframe in self.config['timeframes']:
                await self.collect_data(pair, timeframe, days_back)
        
        await self.close_session()
        self.logger.info("Data collection completed for all pairs and timeframes")

    def run(self, days_back: int = 365):
        """Run the data collection process"""
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Run async collection
        asyncio.run(self.collect_all_data(days_back))

# Example usage
if __name__ == "__main__":
    collector = DataCollector()
    collector.run(days_back=30)  # Collect 30 days of data for testing