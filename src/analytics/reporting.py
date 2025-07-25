# /home/ubuntu/neonadsai_backend/src/analytics/reporting.py

import datetime
from src.integrations import meta_api, linkedin_api, google_ads_api

# Placeholder for storing user credentials/tokens securely
# In a real app, this would involve database lookups based on the logged-in user
USER_CREDENTIALS = {
    "meta": {"access_token": None, "ad_account_id": None},
    "linkedin": {"access_token": None, "account_urn": None},
    "google": {"refresh_token": None, "customer_id": None, "login_customer_id": None}
}

def set_user_credentials(platform, credentials):
    """Placeholder function to update user credentials (same as in campaign_manager)."""
    if platform in USER_CREDENTIALS:
        USER_CREDENTIALS[platform].update(credentials)
        print(f"Updated credentials for {platform} in reporting module")
    else:
        print(f"Warning: Unknown platform {platform}")

def get_multi_platform_performance(platforms, date_preset="last_7d", campaign_ids=None):
    """Fetches aggregated performance data from selected platforms."""
    # campaign_ids should be a dict like {"meta": ["id1"], "google": ["id2"], "linkedin": ["group_id3"]}
    if campaign_ids is None:
        campaign_ids = {}
    
    aggregated_data = {
        "meta": [],
        "linkedin": [],
        "google": [],
        "summary": {"impressions": 0, "clicks": 0, "spend": 0.0}
    }

    # Map date_preset to specific formats if needed
    # Google Ads uses specific keywords like LAST_7_DAYS
    # Meta uses presets like last_7d
    # LinkedIn requires date ranges

    # TODO: Implement proper date range calculation for LinkedIn
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7) # Example for last_7d
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if "meta" in platforms:
        print("--- Fetching Meta Performance --- ")
        meta_creds = USER_CREDENTIALS["meta"]
        if meta_creds.get("access_token"):
            if meta_api.initialize_meta_api(meta_creds["access_token"]):
                meta_campaign_ids = campaign_ids.get("meta", [])
                # Fetch for specific campaigns or all if none provided (API might require specific IDs)
                # For simplicity, fetching for one campaign if provided, else skipping detailed fetch
                if meta_campaign_ids:
                    for camp_id in meta_campaign_ids:
                        insights = meta_api.get_campaign_insights(camp_id, date_preset=date_preset)
                        if insights:
                            for insight in insights:
                                aggregated_data["meta"].append(insight) # Store raw insight
                                aggregated_data["summary"]["impressions"] += int(insight.get("impressions", 0))
                                aggregated_data["summary"]["clicks"] += int(insight.get("clicks", 0))
                                aggregated_data["summary"]["spend"] += float(insight.get("spend", 0.0))
                        else:
                             print(f"Could not fetch insights for Meta campaign {camp_id}")
                else:
                    print("Meta campaign IDs not provided, skipping detailed fetch.")
            else:
                print("Failed to initialize Meta API for reporting.")
        else:
            print("Missing Meta credentials for reporting.")

    if "linkedin" in platforms:
        print("--- Fetching LinkedIn Performance --- ")
        linkedin_creds = USER_CREDENTIALS["linkedin"]
        if linkedin_creds.get("access_token") and linkedin_creds.get("account_urn"):
            # LinkedIn API client is initialized globally
            # Requires r_ads_reporting scope
            # Fetch analytics for the account
            analytics = linkedin_api.get_linkedin_campaign_analytics(
                account_urn=linkedin_creds["account_urn"],
                start_date_str=start_date_str,
                end_date_str=end_date_str
                # Pass access_token if needed
            )
            if analytics is not None: # Check for None explicitly
                aggregated_data["linkedin"] = analytics # Store raw analytics data
                # TODO: Parse LinkedIn analytics and add to summary (structure depends on actual API response)
                print(f"LinkedIn analytics fetched (Placeholder data: {analytics}). Parsing TBD.")
                # Example parsing (assuming structure like [{impressions: 100, clicks: 5, costInLocalCurrency: 10.50}, ...])
                # for item in analytics:
                #     aggregated_data["summary"]["impressions"] += int(item.get("impressions", 0))
                #     aggregated_data["summary"]["clicks"] += int(item.get("clicks", 0))
                #     aggregated_data["summary"]["spend"] += float(item.get("costInLocalCurrency", 0.0))
            else:
                print("Failed to fetch LinkedIn analytics (Placeholder function used).")
        else:
            print("Missing LinkedIn credentials for reporting.")

    if "google" in platforms:
        print("--- Fetching Google Ads Performance --- ")
        google_creds = USER_CREDENTIALS["google"]
        if google_creds.get("refresh_token") and google_creds.get("customer_id"):
            client = google_ads_api.get_google_ads_client(google_creds["refresh_token"], google_creds.get("login_customer_id"))
            if client:
                google_campaign_ids = campaign_ids.get("google", [])
                # Map generic date preset to Google Ads format
                google_date_range = date_preset.upper() # e.g., LAST_7_DAYS
                performance = google_ads_api.get_google_campaign_performance(
                    client=client,
                    customer_id=google_creds["customer_id"],
                    campaign_ids=google_campaign_ids if google_campaign_ids else None,
                    date_range=google_date_range
                )
                if performance:
                    aggregated_data["google"] = performance # Store raw performance data
                    for item in performance:
                        aggregated_data["summary"]["impressions"] += int(item.get("impressions", 0))
                        aggregated_data["summary"]["clicks"] += int(item.get("clicks", 0))
                        # Google Ads cost is in micros, convert to standard currency unit
                        aggregated_data["summary"]["spend"] += float(item.get("cost_micros", 0)) / 1_000_000
                else:
                    print("Failed to fetch Google Ads performance.")
            else:
                print("Failed to initialize Google Ads client for reporting.")
        else:
            print("Missing Google Ads credentials for reporting.")

    print("--- Multi-platform performance fetching finished --- ")
    # Round spend to 2 decimal places
    aggregated_data["summary"]["spend"] = round(aggregated_data["summary"]["spend"], 2)
    return aggregated_data

# Example Usage (requires setting credentials first)
# if __name__ == '__main__':
#     # Dummy credentials for testing structure
#     set_user_credentials("meta", {"access_token": "dummy_meta_token", "ad_account_id": "act_123"})
#     set_user_credentials("linkedin", {"access_token": "dummy_li_token", "account_urn": "urn:li:organization:456"})
#     set_user_credentials("google", {"refresh_token": "dummy_gg_refresh", "customer_id": "789", "login_customer_id": "111"})
#
#     # Example: Fetch performance for specific campaigns created earlier
#     campaign_ids_to_fetch = {
#         "meta": ["meta_campaign_id_1"], # Replace with actual ID from creation step
#         "google": ["google_campaign_id_1"], # Replace with actual ID
#         # "linkedin": ["linkedin_campaign_group_id_1"] # Replace with actual ID
#     }
#
#     performance_data = get_multi_platform_performance(
#         platforms=["meta", "google"], # Select platforms
#         date_preset="last_7d",
#         campaign_ids=campaign_ids_to_fetch
#     )
#
#     print("\n=== Performance Data ===")
#     import json
#     print(json.dumps(performance_data, indent=2))

