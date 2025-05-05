import flet as ft
import time
import datetime

class ChatScreen(ft.Container):
    def __init__(self, app):
        self.app = app
        self.messages = []
        self.emergency_contacts = [
            {"name": "Police", "role": "Emergency Services", "online": True},
            {"name": "Ambulance", "role": "Emergency Services", "online": True},
            {"name": "Fire Department", "role": "Emergency Services", "online": False},
            {"name": "SafeWayAI Support", "role": "Support", "online": True},
        ]

        # Create the chat input
        self.message_input = ft.TextField(
            hint_text="Type a message...",
            border_radius=8,
            filled=True,
            expand=True,
            on_submit=self.send_message,
        )

        # Create the send button
        self.send_button = ft.IconButton(
            icon=ft.icons.SEND,
            icon_color=ft.colors.BLUE,
            on_click=self.send_message,
        )

        # Create the messages list
        self.messages_list = ft.ListView(
            spacing=10,
            auto_scroll=True,
            expand=True,
        )

        # Create the contacts list
        self.contacts_list = ft.ListView(
            spacing=2,
            width=250,
        )

        # Add emergency contacts
        for contact in self.emergency_contacts:
            self.add_contact(contact)

        # Add some initial messages
        self.add_system_message("Welcome to SafeWayAI Emergency Chat")
        self.add_system_message("You can communicate with emergency services here")
        self.add_system_message("In case of emergency, please provide your location and the nature of the emergency")

        # Create the main layout
        super().__init__(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Emergency Chat", size=24, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(left=20, top=20, bottom=10),
                    ),
                    ft.Row(
                        [
                            # Contacts panel
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Container(
                                            content=ft.Text("Contacts", weight=ft.FontWeight.BOLD),
                                            padding=10,
                                        ),
                                        self.contacts_list,
                                    ],
                                ),
                                width=250,
                                bgcolor=ft.colors.BLUE_GREY_50,
                                border_radius=ft.border_radius.only(top_right=8),
                            ),

                            # Chat panel
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Messages area
                                        ft.Container(
                                            content=self.messages_list,
                                            expand=True,
                                            bgcolor=ft.colors.WHITE,
                                            border_radius=8,
                                            padding=10,
                                        ),

                                        # Input area
                                        ft.Container(
                                            content=ft.Row(
                                                [
                                                    self.message_input,
                                                    self.send_button,
                                                ],
                                                spacing=10,
                                            ),
                                            padding=10,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                expand=True,
                                bgcolor=ft.colors.BLUE_GREY_100,
                                padding=10,
                                border_radius=ft.border_radius.only(top_left=8),
                            ),
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            expand=True,
        )

    def add_contact(self, contact):
        """Add a contact to the contacts list"""
        self.contacts_list.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(contact["name"][0]),
                            bgcolor=ft.colors.BLUE if contact["online"] else ft.colors.GREY,
                            radius=15,
                        ),
                        ft.Column(
                            [
                                ft.Text(contact["name"], weight=ft.FontWeight.BOLD),
                                ft.Text(contact["role"], size=12, color=ft.colors.GREY),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Container(
                            width=10,
                            height=10,
                            border_radius=5,
                            bgcolor=ft.colors.GREEN if contact["online"] else ft.colors.GREY,
                            margin=ft.margin.only(left=5),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
                border_radius=8,
                on_click=lambda e, name=contact["name"]: self.select_contact(name),
            )
        )

    def select_contact(self, name):
        """Select a contact to chat with"""
        self.add_system_message(f"You are now chatting with {name}")

    def add_message(self, text, is_user=True):
        """Add a message to the chat"""
        current_time = datetime.datetime.now().strftime("%H:%M")

        self.messages_list.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(text),
                            bgcolor=ft.colors.BLUE if is_user else ft.colors.GREY_300,
                            padding=10,
                            border_radius=ft.border_radius.only(
                                top_left=8,
                                top_right=8,
                                bottom_left=0 if is_user else 8,
                                bottom_right=8 if is_user else 0,
                            ),
                        ),
                        ft.Text(
                            current_time,
                            size=10,
                            color=ft.colors.GREY,
                        ),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.END if is_user else ft.CrossAxisAlignment.START,
                ),
                alignment=ft.alignment.center_right if is_user else ft.alignment.center_left,
                padding=ft.padding.only(left=50 if is_user else 0, right=0 if is_user else 50),
            )
        )

        self.messages.append({"text": text, "is_user": is_user, "time": current_time})

    def add_system_message(self, text):
        """Add a system message to the chat"""
        self.messages_list.controls.append(
            ft.Container(
                content=ft.Text(
                    text,
                    italic=True,
                    size=12,
                    color=ft.colors.GREY,
                ),
                alignment=ft.alignment.center,
                padding=5,
            )
        )

    def send_message(self, e):
        """Send a message"""
        if not self.message_input.value:
            return

        # Add the user message
        self.add_message(self.message_input.value, is_user=True)

        # Clear the input
        message = self.message_input.value
        self.message_input.value = ""

        # Simulate a response after a short delay
        self.simulate_response(message)

    def simulate_response(self, user_message):
        """Simulate a response from the emergency service"""
        # In a real app, this would send the message to a server
        # and receive a response from the emergency service

        # For now, we'll just simulate a response based on keywords
        if "help" in user_message.lower() or "emergency" in user_message.lower():
            response = "We've received your emergency request. Please provide your exact location and the nature of the emergency."
        elif "location" in user_message.lower() or "address" in user_message.lower():
            response = "Thank you for providing your location. Emergency services have been dispatched to your area. Please stay on the line."
        elif "fire" in user_message.lower():
            response = "Fire department has been notified. Please evacuate the building if it's safe to do so and wait for emergency services."
        elif "medical" in user_message.lower() or "ambulance" in user_message.lower():
            response = "Medical emergency services are on their way. Please provide details about the medical condition."
        elif "police" in user_message.lower() or "crime" in user_message.lower():
            response = "Police have been notified. Please find a safe location and wait for officers to arrive."
        else:
            response = "Thank you for your message. How can we assist you with your emergency?"

        # Add a typing indicator
        typing_indicator = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.colors.GREY,
                        animate=ft.animation.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
                    ),
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.colors.GREY,
                        animate=ft.animation.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
                    ),
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.colors.GREY,
                        animate=ft.animation.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            alignment=ft.alignment.center_left,
        )

        self.messages_list.controls.append(typing_indicator)

        # Simulate typing delay
        time.sleep(1.5)

        # Remove typing indicator
        self.messages_list.controls.remove(typing_indicator)

        # Add the response
        self.add_message(response, is_user=False)
