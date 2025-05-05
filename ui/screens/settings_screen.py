import flet as ft
import json
import os

class SettingsScreen(ft.Container):
    def __init__(self, app):
        self.app = app

        # Check if user is admin
        self.is_admin = False
        if hasattr(app, 'data_manager') and hasattr(app.data_manager, 'current_user') and app.data_manager.current_user:
            self.is_admin = app.data_manager.current_user.get('role') == 'admin'

        # Create settings controls
        self.theme_switch = ft.Switch(
            label="Dark Theme",
            value=False,
            on_change=self.toggle_theme,
        )

        self.notification_switch = ft.Switch(
            label="Enable Notifications",
            value=True,
        )

        self.sms_alerts_switch = ft.Switch(
            label="SMS Alerts",
            value=True,
        )

        self.authority_alerts_switch = ft.Switch(
            label="Authority Alerts",
            value=True,
        )

        self.check_interval = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            label="Safety Check Interval: {value} minutes",
            value=5,
        )

        self.alert_sensitivity = ft.Slider(
            min=0,
            max=100,
            divisions=10,
            label="Alert Sensitivity: {value}%",
            value=50,
        )

        # User profile fields
        self.full_name = ft.TextField(
            label="Full Name",
            hint_text="Enter your full name",
            border_radius=8,
            filled=True,
            width=300,
        )

        self.email = ft.TextField(
            label="Email Address",
            hint_text="Enter your email address",
            border_radius=8,
            filled=True,
            width=300,
        )

        self.phone_number = ft.TextField(
            label="Phone Number",
            hint_text="Enter your phone number",
            border_radius=8,
            filled=True,
            width=300,
        )

        # Emergency contacts
        self.emergency_contacts = []
        self.emergency_contacts_list = ft.ListView(
            spacing=10,
            height=200,
            width=400,
            controls=[
                ft.Text("No emergency contacts added yet.", italic=True, color="grey")
            ]
        )

        self.add_contact_button = ft.ElevatedButton(
            text="Add Emergency Contact",
            icon=ft.icons.PERSON_ADD,
            on_click=self.add_emergency_contact,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(15),
            ),
        )

        # Create API key settings
        self.subscription_key = ft.TextField(
            label="Azure Subscription Key",
            password=True,
            can_reveal_password=True,
        )

        self.maps_key = ft.TextField(
            label="Azure Maps Key",
            password=True,
            can_reveal_password=True,
        )

        self.speech_key = ft.TextField(
            label="Azure Speech Key",
            password=True,
            can_reveal_password=True,
        )

        self.functions_url = ft.TextField(
            label="Azure Functions URL",
        )

        self.functions_key = ft.TextField(
            label="Azure Functions Key",
            password=True,
            can_reveal_password=True,
        )

        # Create Cosmos DB settings
        self.cosmos_endpoint = ft.TextField(
            label="Azure Cosmos DB Endpoint",
            hint_text="https://your-account.documents.azure.com:443/",
            width=400,
        )

        self.cosmos_key = ft.TextField(
            label="Azure Cosmos DB Key",
            password=True,
            can_reveal_password=True,
            width=400,
        )

        self.cosmos_database = ft.TextField(
            label="Azure Cosmos DB Database ID",
            hint_text="safewayai",
            width=300,
        )

        self.initialize_db_button = ft.ElevatedButton(
            text="Initialize Database",
            icon=ft.icons.STORAGE,
            on_click=self.initialize_database,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(15),
            ),
        )

        # Load current settings
        self.load_settings()

        # Create save button
        self.save_button = ft.ElevatedButton(
            text="Save Settings",
            icon=ft.icons.SAVE,
            on_click=self.save_settings,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(20),
            ),
        )

        # Create the main layout
        super().__init__(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                                ft.Divider(),

                                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD),
                                self.theme_switch,
                                ft.Divider(),

                                ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD),
                                self.notification_switch,
                                self.sms_alerts_switch,
                                self.authority_alerts_switch,
                                ft.Divider(),

                                ft.Text("Safety", size=18, weight=ft.FontWeight.BOLD),
                                self.check_interval,
                                self.alert_sensitivity,
                                ft.Divider(),

                                ft.Text("User Profile", size=18, weight=ft.FontWeight.BOLD),
                                self.full_name,
                                self.email,
                                self.phone_number,
                                ft.Divider(),

                                ft.Text("Emergency Contacts", size=18, weight=ft.FontWeight.BOLD),
                                self.emergency_contacts_list,
                                self.add_contact_button,
                                ft.Divider(),

                                ft.Container(
                                    content=ft.ExpansionPanel(
                                        header=ft.ListTile(
                                            title=ft.Text("Advanced Settings (Admin Only)"),
                                            subtitle=ft.Text("API Keys and Database Configuration"),
                                        ),
                                        content=ft.Column([
                                            ft.Text("API Keys", size=16, weight=ft.FontWeight.BOLD),
                                            self.subscription_key,
                                            self.maps_key,
                                            self.speech_key,
                                            self.functions_url,
                                            self.functions_key,
                                            ft.Divider(),

                                            ft.Text("Cosmos DB Settings", size=16, weight=ft.FontWeight.BOLD),
                                            self.cosmos_endpoint,
                                            self.cosmos_key,
                                            self.cosmos_database,
                                            self.initialize_db_button,
                                        ]),
                                        expanded=False,
                                    ),
                                    visible=self.is_admin,
                                ),
                                ft.Divider(),

                                self.save_button,
                            ],
                            spacing=16,
                        ),
                        padding=20,
                        border_radius=8,
                        bgcolor=ft.colors.WHITE,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.colors.BLACK12,
                        ),
                    ),
                ],
                spacing=16,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )

    def toggle_theme(self, e):
        # Toggle theme mode
        if e.control.value:
            self.app.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
        self.app.page.update()

    def load_settings(self):
        # Load Azure config
        config_path = os.path.join('config', 'azure_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)

                # Set API key fields
                self.subscription_key.value = config.get("subscription_key", "")

                if "maps" in config:
                    self.maps_key.value = config["maps"].get("subscription_key", "")

                if "ai_services" in config:
                    self.speech_key.value = config["ai_services"].get("speech_key", "")

                if "functions" in config:
                    self.functions_url.value = config["functions"].get("base_url", "")
                    self.functions_key.value = config["functions"].get("api_key", "")

                # Set Cosmos DB fields
                if "cosmos_db" in config:
                    self.cosmos_endpoint.value = config["cosmos_db"].get("endpoint", "")
                    self.cosmos_key.value = config["cosmos_db"].get("key", "")
                    self.cosmos_database.value = config["cosmos_db"].get("database_id", "safewayai")

                # Load user profile and emergency contacts
                if "user_profile" in config:
                    self.full_name.value = config["user_profile"].get("full_name", "")
                    self.email.value = config["user_profile"].get("email", "")
                    self.phone_number.value = config["user_profile"].get("phone_number", "")

                if "emergency_contacts" in config:
                    self.emergency_contacts = config["emergency_contacts"]
                    self.update_emergency_contacts_list()

                # Load app settings
                if "app_settings" in config:
                    self.theme_switch.value = config["app_settings"].get("dark_theme", False)
                    self.notification_switch.value = config["app_settings"].get("notifications_enabled", True)
                    self.sms_alerts_switch.value = config["app_settings"].get("sms_alerts_enabled", True)
                    self.authority_alerts_switch.value = config["app_settings"].get("authority_alerts_enabled", True)
                    self.check_interval.value = config["app_settings"].get("check_interval", 5)
                    self.alert_sensitivity.value = config["app_settings"].get("alert_sensitivity", 50)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_settings(self, e):
        # Save Azure config
        config_path = os.path.join('config', 'azure_config.json')
        try:
            # Load existing config if it exists
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Update config with new values
            config["subscription_key"] = self.subscription_key.value

            if "maps" not in config:
                config["maps"] = {}
            config["maps"]["subscription_key"] = self.maps_key.value

            if "ai_services" not in config:
                config["ai_services"] = {}
            config["ai_services"]["speech_key"] = self.speech_key.value

            if "functions" not in config:
                config["functions"] = {}
            config["functions"]["base_url"] = self.functions_url.value
            config["functions"]["api_key"] = self.functions_key.value

            # Update Cosmos DB settings
            if "cosmos_db" not in config:
                config["cosmos_db"] = {}
            config["cosmos_db"]["endpoint"] = self.cosmos_endpoint.value
            config["cosmos_db"]["key"] = self.cosmos_key.value
            config["cosmos_db"]["database_id"] = self.cosmos_database.value or "safewayai"

            # Update user profile
            if "user_profile" not in config:
                config["user_profile"] = {}
            config["user_profile"]["full_name"] = self.full_name.value
            config["user_profile"]["email"] = self.email.value
            config["user_profile"]["phone_number"] = self.phone_number.value

            # Update emergency contacts
            config["emergency_contacts"] = self.emergency_contacts

            # Update app settings
            if "app_settings" not in config:
                config["app_settings"] = {}
            config["app_settings"]["dark_theme"] = self.theme_switch.value
            config["app_settings"]["notifications_enabled"] = self.notification_switch.value
            config["app_settings"]["sms_alerts_enabled"] = self.sms_alerts_switch.value
            config["app_settings"]["authority_alerts_enabled"] = self.authority_alerts_switch.value
            config["app_settings"]["check_interval"] = self.check_interval.value
            config["app_settings"]["alert_sensitivity"] = self.alert_sensitivity.value

            # Ensure config directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # Show success message
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully!"),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()
        except Exception as e:
            print(f"Error saving config: {e}")

            # Show error message
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error saving settings: {e}"),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()

    def add_emergency_contact(self, _):
        """Add a new emergency contact."""
        # Create a dialog for adding a new contact
        def close_dlg(_):
            dialog.open = False
            self.app.page.update()

        def add_contact(_):
            name = name_field.value
            phone = phone_field.value
            relationship = relationship_field.value

            if not name or not phone:
                error_text.value = "Name and phone number are required"
                error_text.visible = True
                self.app.page.update()
                return

            # Add the contact to the list
            contact = {
                "name": name,
                "phone": phone,
                "relationship": relationship
            }
            self.emergency_contacts.append(contact)

            # Update the UI
            self.update_emergency_contacts_list()

            # Close the dialog
            dialog.open = False
            self.app.page.update()

        # Create the dialog fields
        name_field = ft.TextField(
            label="Name",
            hint_text="Contact name",
            border_radius=8,
            filled=True,
            width=300,
        )

        phone_field = ft.TextField(
            label="Phone Number",
            hint_text="Contact phone number",
            border_radius=8,
            filled=True,
            width=300,
        )

        relationship_field = ft.Dropdown(
            label="Relationship",
            hint_text="Select relationship",
            options=[
                ft.dropdown.Option("Family"),
                ft.dropdown.Option("Friend"),
                ft.dropdown.Option("Colleague"),
                ft.dropdown.Option("Other"),
            ],
            width=300,
        )

        error_text = ft.Text(
            value="",
            color="red",
            size=14,
            visible=False,
        )

        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add Emergency Contact"),
            content=ft.Column(
                [
                    name_field,
                    phone_field,
                    relationship_field,
                    error_text,
                ],
                spacing=10,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Add", on_click=add_contact),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show the dialog
        self.app.page.dialog = dialog
        dialog.open = True
        self.app.page.update()

    def update_emergency_contacts_list(self):
        """Update the emergency contacts list UI."""
        # Clear the current list
        self.emergency_contacts_list.controls.clear()

        # Check if there are any contacts
        if not self.emergency_contacts:
            self.emergency_contacts_list.controls.append(
                ft.Text("No emergency contacts added yet.", italic=True, color="grey")
            )
        else:
            # Add each contact to the list
            for i, contact in enumerate(self.emergency_contacts):
                self.emergency_contacts_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.PERSON),
                                            ft.Text(contact["name"], weight=ft.FontWeight.BOLD),
                                            ft.Text(f" - {contact.get('relationship', 'Other')}", italic=True),
                                        ]
                                    ),
                                    ft.Text(contact["phone"]),
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.icons.DELETE,
                                                tooltip="Delete contact",
                                                on_click=lambda _, idx=i: self.delete_contact(idx),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                        ),
                    )
                )

        # Update the UI
        self.app.page.update()

    def delete_contact(self, index):
        """Delete an emergency contact."""
        if 0 <= index < len(self.emergency_contacts):
            del self.emergency_contacts[index]
            self.update_emergency_contacts_list()

    def initialize_database(self, e):
        """Initialize the Cosmos DB database with default data."""
        try:
            from services.azure_cosmos import AzureCosmos

            # Save settings first to ensure Cosmos DB config is up to date
            self.save_settings(None)

            # Initialize the database
            result = AzureCosmos.initialize_database()

            # Show success message
            message = f"Database initialized successfully! Created {result['users_created']} users and {result['incidents_created']} incidents."
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()
        except Exception as e:
            # Show error message
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error initializing database: {e}"),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()