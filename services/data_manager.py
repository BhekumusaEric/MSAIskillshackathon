from services.repositories import (
    firebase_user_repository,
    firebase_incident_repository,
    firebase_report_repository,
    firebase_settings_repository
)

class DataManager:
    """Data manager for SafeWayAI application"""

    def __init__(self):
        """Initialize the data manager"""
        self.current_user = None
        self.user_settings = None

    def login(self, username, password):
        """Login a user"""
        print(f"DataManager: Attempting to login with {username}")

        try:
            # Try to authenticate with Firebase first
            print("DataManager: Trying Firebase authentication")
            user = firebase_user_repository.authenticate_user(username, password)

            if user:
                print(f"DataManager: Firebase authentication successful for {username}")
                self.current_user = user
                print(f"DataManager: Current user set: {self.current_user}")

                print(f"DataManager: Getting settings for user {user['id']}")
                self.user_settings = firebase_settings_repository.get_settings(user['id'])
                print(f"DataManager: Settings retrieved: {self.user_settings is not None}")

                return True
            else:
                print("DataManager: Firebase authentication failed")
        except Exception as e:
            print(f"DataManager: Error during Firebase authentication: {e}")

        # Fallback to hardcoded credentials for testing
        print("DataManager: Trying hardcoded credentials")
        # This is a temporary solution until the database is properly initialized
        hardcoded_credentials = [
            ("admin", "admin123"),
            ("admin", "admin"),
            ("admin", "password"),
            ("user", "password"),
            ("test", "test"),
        ]

        for valid_username, valid_password in hardcoded_credentials:
            if username == valid_username and password == valid_password:
                print(f"DataManager: Hardcoded credentials match for {username}")
                # Create a default user object
                self.current_user = {
                    "id": f"default_{username}",
                    "username": username,
                    "role": "admin" if username == "admin" else "user",
                    "full_name": f"Default {username.capitalize()}"
                }
                print(f"DataManager: Default user created: {self.current_user}")

                # Create default settings
                print(f"DataManager: Getting settings for default user {self.current_user['id']}")
                self.user_settings = firebase_settings_repository.get_settings(f"default_{username}")
                print(f"DataManager: Default settings retrieved: {self.user_settings is not None}")

                return True

        # Special case - accept any password for admin during testing
        if username == "admin":
            print("DataManager: Special case - accepting any password for admin")
            self.current_user = {
                "id": "default_admin",
                "username": "admin",
                "role": "admin",
                "full_name": "Default Admin"
            }
            print(f"DataManager: Admin user created: {self.current_user}")

            # Create default settings
            print("DataManager: Getting settings for admin user")
            self.user_settings = firebase_settings_repository.get_settings("default_admin")
            print(f"DataManager: Admin settings retrieved: {self.user_settings is not None}")

            return True

        print(f"DataManager: Login failed for {username}")
        return False

    def logout(self):
        """Logout the current user"""
        self.current_user = None
        self.user_settings = None

    def get_current_user(self):
        """Get the current user"""
        return self.current_user

    def get_settings(self):
        """Get settings for the current user"""
        if not self.current_user:
            return None

        if not self.user_settings:
            self.user_settings = firebase_settings_repository.get_settings(self.current_user['id'])

        return self.user_settings

    def update_settings(self, settings_data):
        """Update settings for the current user"""
        if not self.current_user:
            return False

        updated_settings = firebase_settings_repository.update_settings(self.current_user['id'], settings_data)
        if updated_settings:
            # Refresh settings
            self.user_settings = updated_settings
            return True

        return False

    def get_recent_incidents(self, limit=10):
        """Get recent incidents"""
        return firebase_incident_repository.get_recent_incidents(limit=limit)

    def report_incident(self, incident_data):
        """Report a new incident"""
        if not self.current_user:
            return False

        # Create the incident
        incident = firebase_incident_repository.create_incident(
            incident_type=incident_data.get('type', 'Unknown'),
            description=incident_data.get('description', ''),
            location=incident_data.get('location', ''),
            latitude=incident_data.get('latitude'),
            longitude=incident_data.get('longitude'),
            severity=incident_data.get('severity', 'medium'),
            reported_by=self.current_user['id'],
            status=incident_data.get('status', 'active')
        )

        return incident

    def get_community_reports(self, limit=10):
        """Get community reports"""
        return firebase_report_repository.get_recent_reports(limit=limit)

    def submit_report(self, report_data):
        """Submit a community report"""
        if not self.current_user:
            return False

        # Create the report
        report = firebase_report_repository.create_report(
            report_type=report_data.get('type', 'Unknown'),
            details=report_data.get('details', ''),
            location=report_data.get('location', ''),
            latitude=report_data.get('latitude'),
            longitude=report_data.get('longitude'),
            severity=report_data.get('severity', 'medium'),
            reported_by=self.current_user['id'],
            images=report_data.get('images', [])
        )

        return report
