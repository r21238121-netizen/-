# BingX Trading Bot Setup Instructions

## Prerequisites

Before running the trading bot, you need to configure your API credentials in the `.env` file.

## Setting Up Your API Credentials

1. **Obtain your BingX API keys**:
   - Log in to your BingX account
   - Navigate to the API management section
   - Create a new API key with appropriate permissions

2. **Update the `.env` file**:
   - Open the `.env` file in the project root
   - Replace the placeholder values with your actual API credentials:

   ```env
   BINGX_API_KEY=your_actual_api_key_here
   BINGX_SECRET=your_actual_secret_key_here
   BINGX_MODE=swap  # or spot
   ```

3. **Security considerations**:
   - Never commit the `.env` file to version control
   - Keep your API keys secure and private
   - Only grant the minimum required permissions to your API key

## Running the Bot

Once you've configured your API credentials:

```bash
python run.py
```

## Verification

You can verify your setup using the test script:

```bash
python test_env_init.py
```

This will check that:
- The `.env` file is properly loaded
- API credentials are not using placeholder values
- The BingX client can be initialized successfully

## Troubleshooting

- **Configuration Error**: Make sure your `.env` file contains actual API keys, not placeholder values
- **Connection Issues**: Verify your API keys have the correct permissions
- **Mode Issues**: Ensure you're using the correct mode ("swap" for futures, "spot" for spot trading)