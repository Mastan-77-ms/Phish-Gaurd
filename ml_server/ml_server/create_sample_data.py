import pandas as pd
import random

# A small sample of Safe and Phishing URLs to get you started
data = {
    'URL': [
        # SAFE URLs (Label 0)
        "google.com", "youtube.com", "facebook.com", "baidu.com", "wikipedia.org",
        "reddit.com", "yahoo.com", "amazon.com", "twitter.com", "instagram.com",
        "linkedin.com", "netflix.com", "microsoft.com", "twitch.tv", "stackoverflow.com",
        "github.com", "apple.com", "adobe.com", "wordpress.org", "blogspot.com",
        "dropbox.com", "salesforce.com", "whatsapp.com", "spotify.com", "cnn.com",
        "bbc.co.uk", "nytimes.com", "weather.com", "chase.com", "paypal.com",
        
        # PHISHING / MALICIOUS URLs (Label 1)
        "secure-login-paypal.com", "update-payment-netflix.net", "apple-id-verify.info",
        "wells-fargo-alert.xyz", "amazon-order-status.com.br", "free-crypto-giveaway.io",
        "verify-account-google.tk", "hotmail-login-secure.biz", "facebook-recovery.net",
        "irs-tax-refund-claim.com", "x-verification-badge.cc", "win-iphone-15.site",
        "bank-of-america-alert.us", "coinbase-support-chat.org", "metamask-wallet-connect.io",
        "trust-wallet-validate.com", "binance-login-secure.net", "account-disabled-alert.info",
        "verify-card-details.xyz", "login-microsoft-online.com-secure.ru"
    ],
    'Label': [
        # We need to match the number of URLs above
        # First 30 are safe (good), next 20 are phishing (bad)
        'good'] * 30 + ['bad'] * 20
}

# Create the DataFrame
df = pd.read_csv("https://raw.githubusercontent.com/GregaVrbancic/Phishing-Dataset/master/dataset_small.csv") 
# NOTE: If you have internet, the line above downloads 50,000 real rows from GitHub!
# If that fails, we fall back to the manual list above:
if df.empty:
    print("Could not download from GitHub. Using small manual list...")
    df = pd.DataFrame(data)

# Save to CSV
output_file = "phishing_data.csv"
df.to_csv(output_file, index=False)

print(f"✅ Success! Created '{output_file}' with {len(df)} URLs.")
print("You can now run 'python train_model.py'")