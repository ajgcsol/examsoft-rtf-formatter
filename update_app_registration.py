#!/usr/bin/env python3
"""
Microsoft 365 App Registration Update Script

This script programmatically updates your existing Microsoft 365 app registration
to enable the required permissions for SharePoint integration and 90-day token persistence.

Requirements:
- Azure CLI installed and authenticated (az login)
- Application.ReadWrite.All permission for the user running this script
- The Client ID of your existing app registration

Usage:
    python update_app_registration.py --client-id YOUR_CLIENT_ID

Author: GitHub Copilot
Date: August 1, 2025
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

class AppRegistrationUpdater:
    """Updates Microsoft 365 app registration settings via Azure CLI"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.app_object_id = None
        
    def run_az_command(self, command: List[str]) -> Tuple[bool, str]:
        """Execute Azure CLI command and return success status and output"""
        try:
            print(f"🔧 Running: az {' '.join(command)}")
            result = subprocess.run(
                ['az'] + command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 60 seconds"
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def check_az_login(self) -> bool:
        """Check if user is logged into Azure CLI"""
        print("🔐 Checking Azure CLI authentication...")
        success, output = self.run_az_command(['account', 'show'])
        
        if success:
            account_info = json.loads(output)
            print(f"✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
            print(f"📋 Tenant: {account_info.get('tenantDisplayName', 'Unknown')}")
            return True
        else:
            print("❌ Not logged into Azure CLI")
            print("   Please run: az login")
            return False
    
    def get_app_info(self) -> bool:
        """Get app registration information"""
        print(f"🔍 Looking up app registration with Client ID: {self.client_id}")
        
        success, output = self.run_az_command([
            'ad', 'app', 'show',
            '--id', self.client_id,
            '--query', '{objectId:id,displayName:displayName,appId:appId}'
        ])
        
        if success:
            app_info = json.loads(output)
            self.app_object_id = app_info['objectId']
            print(f"✅ Found app: {app_info['displayName']}")
            print(f"   Object ID: {self.app_object_id}")
            print(f"   App ID: {app_info['appId']}")
            return True
        else:
            print(f"❌ Could not find app registration: {output}")
            return False
    
    def get_current_permissions(self) -> Dict:
        """Get current API permissions"""
        print("📋 Getting current API permissions...")
        
        success, output = self.run_az_command([
            'ad', 'app', 'show',
            '--id', self.client_id,
            '--query', 'requiredResourceAccess'
        ])
        
        if success:
            current_permissions = json.loads(output) or []
            print(f"📊 Current permissions: {len(current_permissions)} resource(s)")
            return current_permissions
        else:
            print(f"❌ Could not get permissions: {output}")
            return []
    
    def add_microsoft_graph_permissions(self) -> bool:
        """Add required Microsoft Graph permissions"""
        print("🔑 Adding Microsoft Graph API permissions...")
        
        # Microsoft Graph resource ID
        graph_resource_id = "00000003-0000-0000-c000-000000000000"
        
        # Required permissions (scopes)
        required_scopes = [
            {
                "id": "37f7f235-527c-4136-accd-4a02d197296e",  # offline_access
                "type": "Scope"
            },
            {
                "id": "863451e7-0667-486c-a5d6-d135439485f0",  # Sites.ReadWrite.All (delegated)
                "type": "Scope"
            },
            {
                "id": "5a54b8b3-347c-476d-8f8e-42d5c7424d29",  # Files.ReadWrite.All (delegated)
                "type": "Scope"
            }
        ]
        
        # Get current permissions to merge
        current_permissions = self.get_current_permissions()
        
        # Find existing Microsoft Graph permissions
        graph_permissions = None
        for perm in current_permissions:
            if perm.get('resourceAppId') == graph_resource_id:
                graph_permissions = perm
                break
        
        if not graph_permissions:
            # Create new Microsoft Graph permissions entry
            graph_permissions = {
                "resourceAppId": graph_resource_id,
                "resourceAccess": required_scopes
            }
            current_permissions.append(graph_permissions)
        else:
            # Merge with existing permissions
            existing_scope_ids = {scope['id'] for scope in graph_permissions.get('resourceAccess', [])}
            for scope in required_scopes:
                if scope['id'] not in existing_scope_ids:
                    graph_permissions['resourceAccess'].append(scope)
        
        # Update the app registration
        permissions_json = json.dumps(current_permissions)
        
        success, output = self.run_az_command([
            'ad', 'app', 'update',
            '--id', self.client_id,
            '--required-resource-accesses', permissions_json
        ])
        
        if success:
            print("✅ Microsoft Graph permissions added successfully")
            return True
        else:
            print(f"❌ Failed to add permissions: {output}")
            return False
    
    def enable_public_client_flows(self) -> bool:
        """Enable public client flows (required for device code flow)"""
        print("🔓 Enabling public client flows...")
        
        success, output = self.run_az_command([
            'ad', 'app', 'update',
            '--id', self.client_id,
            '--is-fallback-public-client', 'true'
        ])
        
        if success:
            print("✅ Public client flows enabled")
            return True
        else:
            print(f"❌ Failed to enable public client flows: {output}")
            return False
    
    def grant_admin_consent(self) -> bool:
        """Grant admin consent for the permissions"""
        print("🔐 Attempting to grant admin consent...")
        
        success, output = self.run_az_command([
            'ad', 'app', 'permission', 'admin-consent',
            '--id', self.client_id
        ])
        
        if success:
            print("✅ Admin consent granted successfully")
            return True
        else:
            print(f"⚠️  Admin consent may require additional permissions: {output}")
            print("   You may need to manually grant consent in the Azure portal")
            return False
    
    def configure_token_lifetime(self) -> bool:
        """Configure token lifetime policies (requires additional permissions)"""
        print("⏰ Configuring token lifetime policies...")
        
        # This requires Policy.ReadWrite.ApplicationConfiguration permission
        # which typically requires Global Admin or higher privileges
        
        policy_definition = {
            "definition": [
                json.dumps({
                    "TokenLifetimePolicy": {
                        "Version": 1,
                        "RefreshTokenMaxInactiveTime": "90.00:00:00",  # 90 days
                        "RefreshTokenMaxAgeSingleFactor": "90.00:00:00"  # 90 days
                    }
                })
            ],
            "displayName": "ExamFormatter90DayTokenPolicy",
            "type": "tokenLifetimePolicy"
        }
        
        # Create the policy
        policy_json = json.dumps(policy_definition)
        
        success, output = self.run_az_command([
            'rest',
            '--method', 'POST',
            '--url', 'https://graph.microsoft.com/v1.0/policies/tokenLifetimePolicies',
            '--body', policy_json,
            '--headers', 'Content-Type=application/json'
        ])
        
        if success:
            try:
                policy_result = json.loads(output)
                policy_id = policy_result.get('id')
                print(f"✅ Token lifetime policy created: {policy_id}")
                
                # Apply policy to the app
                assign_success, assign_output = self.run_az_command([
                    'rest',
                    '--method', 'POST',
                    '--url', f'https://graph.microsoft.com/v1.0/applications/{self.app_object_id}/tokenLifetimePolicies/$ref',
                    '--body', json.dumps({"@odata.id": f"https://graph.microsoft.com/v1.0/policies/tokenLifetimePolicies/{policy_id}"}),
                    '--headers', 'Content-Type=application/json'
                ])
                
                if assign_success:
                    print("✅ Token lifetime policy applied to app")
                    return True
                else:
                    print(f"⚠️  Policy created but could not apply to app: {assign_output}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"⚠️  Policy creation response not parseable: {output}")
                return False
        else:
            print(f"⚠️  Token lifetime policy requires Global Admin permissions: {output}")
            print("   The app will work with default token lifetimes")
            return False
    
    def verify_configuration(self) -> bool:
        """Verify the final configuration"""
        print("\n🔍 Verifying final configuration...")
        
        success, output = self.run_az_command([
            'ad', 'app', 'show',
            '--id', self.client_id,
            '--query', '{displayName:displayName,publicClient:isFallbackPublicClient,permissions:requiredResourceAccess}'
        ])
        
        if success:
            config = json.loads(output)
            print(f"✅ App Name: {config['displayName']}")
            print(f"✅ Public Client Flows: {config['publicClient']}")
            
            # Check for Microsoft Graph permissions
            graph_perms = None
            for perm in config.get('permissions', []):
                if perm.get('resourceAppId') == '00000003-0000-0000-c000-000000000000':
                    graph_perms = perm
                    break
            
            if graph_perms:
                scope_count = len([p for p in graph_perms.get('resourceAccess', []) if p.get('type') == 'Scope'])
                print(f"✅ Microsoft Graph Delegated Permissions: {scope_count}")
            else:
                print("❌ No Microsoft Graph permissions found")
                return False
            
            return True
        else:
            print(f"❌ Could not verify configuration: {output}")
            return False
    
    def update_config_file(self) -> bool:
        """Update the examsoft_m365_config.py file with correct client_id"""
        print("📝 Updating configuration file...")
        
        config_file = "examsoft_m365_config.py"
        
        try:
            # Read current config
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update client_id if it exists
            if 'CLIENT_ID' in content:
                # Simple replacement - you might want to be more sophisticated
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('CLIENT_ID'):
                        lines[i] = f'CLIENT_ID = "{self.client_id}"'
                        break
                
                # Write back
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Updated {config_file} with Client ID")
                return True
            else:
                print(f"⚠️  Could not find CLIENT_ID in {config_file}")
                return False
                
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found")
            return False
        except Exception as e:
            print(f"❌ Error updating config file: {str(e)}")
            return False
    
    def run_update(self) -> bool:
        """Run the complete update process"""
        print("🚀 Starting Microsoft 365 App Registration Update\n")
        
        # Step 1: Check Azure CLI login
        if not self.check_az_login():
            return False
        
        # Step 2: Get app information
        if not self.get_app_info():
            return False
        
        print("\n" + "="*60)
        print("📋 UPDATING APP REGISTRATION SETTINGS")
        print("="*60)
        
        # Step 3: Add Microsoft Graph permissions
        permissions_success = self.add_microsoft_graph_permissions()
        
        # Step 4: Enable public client flows
        public_client_success = self.enable_public_client_flows()
        
        # Step 5: Grant admin consent (may fail if insufficient permissions)
        consent_success = self.grant_admin_consent()
        
        # Step 6: Configure token lifetime (may fail if insufficient permissions)
        token_lifetime_success = self.configure_token_lifetime()
        
        # Step 7: Verify configuration
        verification_success = self.verify_configuration()
        
        # Step 8: Update config file
        config_update_success = self.update_config_file()
        
        print("\n" + "="*60)
        print("📊 UPDATE SUMMARY")
        print("="*60)
        print(f"✅ App Information: {'Success' if self.app_object_id else 'Failed'}")
        print(f"✅ Graph Permissions: {'Success' if permissions_success else 'Failed'}")
        print(f"✅ Public Client Flows: {'Success' if public_client_success else 'Failed'}")
        print(f"⚠️  Admin Consent: {'Success' if consent_success else 'May need manual action'}")
        print(f"⚠️  Token Lifetime: {'Success' if token_lifetime_success else 'May need Global Admin'}")
        print(f"✅ Configuration Verified: {'Success' if verification_success else 'Failed'}")
        print(f"✅ Config File Updated: {'Success' if config_update_success else 'Manual update needed'}")
        
        # Determine overall success
        critical_success = permissions_success and public_client_success and verification_success
        
        if critical_success:
            print("\n🎉 APP REGISTRATION UPDATE SUCCESSFUL!")
            print("\n📋 Next Steps:")
            print("1. Test authentication in your Streamlit app")
            print("2. Try uploading a file to SharePoint")
            print("3. If admin consent is needed, ask your IT admin to:")
            print(f"   - Go to Azure Portal > App Registrations > {self.client_id}")
            print("   - Click 'API permissions' > 'Grant admin consent'")
            
            if not token_lifetime_success:
                print("4. For 90-day token persistence, ask your Global Admin to:")
                print("   - Configure token lifetime policies as shown in app_registration_guide.py")
            
            return True
        else:
            print("\n❌ CRITICAL ERRORS OCCURRED")
            print("Please check the errors above and try again or contact your IT administrator")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Update Microsoft 365 App Registration for SharePoint Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python update_app_registration.py --client-id 12345678-1234-1234-1234-123456789012
    python update_app_registration.py --client-id your-client-id --verify-only
        """
    )
    
    parser.add_argument(
        '--client-id',
        required=True,
        help='The Client ID (Application ID) of your existing Microsoft 365 app registration'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify current configuration without making changes'
    )
    
    args = parser.parse_args()
    
    updater = AppRegistrationUpdater(args.client_id)
    
    if args.verify_only:
        print("🔍 VERIFICATION MODE - No changes will be made\n")
        if updater.check_az_login() and updater.get_app_info():
            updater.verify_configuration()
    else:
        success = updater.run_update()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
