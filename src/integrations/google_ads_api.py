# /home/ubuntu/neonadsai_backend/src/integrations/google_ads_api.py

import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# TODO: Load Developer Token, Client ID, Client Secret, Refresh Token securely
# These might be stored per-user or globally depending on the app design.
# The google-ads.yaml configuration file is the standard way, but we might need
# to manage credentials programmatically for multiple users.

# Placeholder for programmatic configuration or loading from a central config
# For development, a google-ads.yaml in the home directory is often used.
DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
# login_customer_id is needed for accessing manager accounts, can be optional otherwise
LOGIN_CUSTOMER_ID = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", None)

def get_google_ads_client(refresh_token, login_customer_id=None):
    """Initializes and returns a Google Ads API client instance."""
    try:
        credentials = {
            "developer_token": DEVELOPER_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
            "login_customer_id": login_customer_id,
            "use_proto_plus": True # Recommended setting
        }
        # Initialize client using dictionary configuration
        googleads_client = GoogleAdsClient.load_from_dict(credentials)
        print("Google Ads API Client Initialized Successfully.")
        return googleads_client
    except Exception as e:
        print(f"Error initializing Google Ads client: {e}")
        return None

def get_accessible_customers(client):
    """Lists customers accessible by the authenticated user."""
    try:
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        customer_ids = []
        for resource_name in accessible_customers.resource_names:
            # resource_name is like "customers/1234567890"
            customer_id = resource_name.split("/")[-1]
            # Optionally, fetch customer details here if needed
            customer_ids.append(customer_id)
        print(f"Found accessible customers: {customer_ids}")
        return customer_ids
    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name} and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message \"{error.message}\".")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        print(f"Error listing accessible customers: {e}")
        return None

def create_google_campaign(client, customer_id, name, budget_micros, status=\"PAUSED\"):
    """Creates a new campaign in the specified customer account."""
    # This is a simplified example for a Search campaign
    try:
        # 1. Create a budget
        campaign_budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"Budget for {name} #{os.urandom(4).hex()}"
        budget.delivery_method = client.get_type("BudgetDeliveryMethodEnum").BudgetDeliveryMethod.STANDARD
        budget.amount_micros = budget_micros # e.g., 5000000 for $5

        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        print(f"Created budget: {budget_resource_name}")

        # 2. Create the campaign
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = name
        campaign.advertising_channel_type = client.get_type(
            "AdvertisingChannelTypeEnum"
        ).AdvertisingChannelType.SEARCH
        campaign.status = client.get_type("CampaignStatusEnum").CampaignStatus.Value(status)
        # Set bidding strategy (Manual CPC example)
        campaign.manual_cpc.enhanced_cpc_enabled = True
        # Set budget
        campaign.campaign_budget = budget_resource_name
        # Set targeting (optional, add later)
        campaign.network_settings.target_google_search = True
        campaign.network_settings.target_search_network = True
        campaign.network_settings.target_content_network = False
        campaign.network_settings.target_partner_search_network = False

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name
        campaign_id = campaign_resource_name.split("/")[-1]
        print(f"Created campaign: {campaign_resource_name} (ID: {campaign_id})")
        return campaign_id

    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name} and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message \"{error.message}\".")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        print(f"Error creating Google Ads campaign: {e}")
        return None

def get_google_campaign_performance(client, customer_id, campaign_ids=None, date_range="LAST_7_DAYS"):
    """Fetches performance metrics for campaigns."""
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING {date_range}
    """
    if campaign_ids:
        query += f" AND campaign.id IN ({', '.join(map(str, campaign_ids))})"

    try:
        search_request = client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        stream = ga_service.search_stream(search_request)

        results = []
        for batch in stream:
            for row in batch.results:
                results.append({
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost_micros": row.metrics.cost_micros
                })
        print(f"Fetched performance for {len(results)} campaign(s)")
        return results

    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name} and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message \"{error.message}\".")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        return None
    except Exception as e:
        print(f"Error fetching Google Ads performance: {e}")
        return None

# Example Usage (requires valid credentials and client initialization)
# if __name__ == '__main__':
#     # Assume REFRESH_TOKEN is obtained via OAuth flow
#     client = get_google_ads_client(REFRESH_TOKEN, LOGIN_CUSTOMER_ID)
#     if client:
#         customers = get_accessible_customers(client)
#         if customers:
#             target_customer_id = customers[0] # Select the appropriate customer ID
#             print(f"Using customer ID: {target_customer_id}")
#             # new_campaign_id = create_google_campaign(client, target_customer_id, "Test API Search Campaign", 5000000) # $5 budget
#             # if new_campaign_id:
#             #     performance = get_google_campaign_performance(client, target_customer_id, [new_campaign_id])
#             #     print(performance)
#             performance_all = get_google_campaign_performance(client, target_customer_id)
#             print(performance_all)

