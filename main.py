from dotenv import load_dotenv
import os
import json

from typing import List
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from tool_functions import (
check_doctor_exists,
get_doctor_by_department,
create_patient,
book_appointment,
get_patient_by_phone,
get_available_slots,
is_slot_available
)

# =========================

# Load Environment Variables

# =========================

load_dotenv()

# =========================

# OpenAI Client

# =========================

client = OpenAI(
api_key=os.getenv("OPENAI_API_KEY")
)

# =========================

# Startup Messages

# =========================

print("Healthcare Chatbot Started")
print("Type 'exit' to stop.\n")

print("Shini: Hello, welcome to Super Clinic.")
print("Shini: How may I assist you today?\n")

# =========================

# Conversation Memory

# =========================

messages: List[ChatCompletionMessageParam] = [
{
"role": "system",
"content": (
"You are Shini, an intelligent healthcare assistant "
"for Super Clinic.\n\n"

"Your Responsibilities:\n"
"- Understand patient symptoms.\n"
"- Identify the correct medical department.\n"
"- Recommend suitable doctors.\n"
"- Check appointment availability.\n"
"- Register new patients.\n"
"- Book appointments using tools.\n"
"- Never confirm appointments unless booking succeeds.\n"
"- Be professional, warm and concise.\n\n"


"Department Rules:\n"
"- Only recommend departments available in Super Clinic.\n"
"- Do not invent new departments.\n"
"- If symptoms are unclear, ask one short follow-up question.\n"
"- After identifying symptoms, directly recommend one department.\n"

"Booking Workflow Rules:\n"
"- You ARE capable of registering patients.\n"
"- You ARE capable of booking appointments.\n"
"- Use create_patient for new patients.\n"
"- Use get_patient_by_phone for existing patients.\n"
"- Use get_doctor_by_department when symptoms are identified.\n"
"- Use check_doctor_exists if user mentions doctor name.\n"
"- Use get_available_slots before appointment confirmation.\n"
"- Use is_slot_available before booking.\n"
"- Use book_appointment to finalize bookings.\n"
"- Never tell users to contact reception.\n"
"- Never say you lack capability.\n"
"- Complete the booking workflow yourself.\n\n"

"Conversation Rules:\n"
"- Keep responses short and natural.\n"
"- Prefer replies under 2 sentences.\n"
"- Avoid long explanations.\n"
"- Ask only necessary questions.\n"
"- Avoid repeating information.\n"
"- Avoid unnecessary confirmations like 'okay'.\n"
"- Continue workflow once enough details are available.\n\n"

"Date and Time Rules:\n"
"- If user says 'today' or 'tomorrow', always mention the exact date in confirmations.\n"
"- Always confirm appointment date and time clearly.\n"
"- Never assume unavailable slots are free.\n\n"

"Final Confirmation Format:\n"
"- Doctor Name\n"
"- Department\n"
"- Appointment Date\n"
"- Appointment Time\n"
"- Patient ID\n\n"

"Example Confirmation:\n"
"'Your appointment with Dr. Vikram Mehta "
"(Orthopedics) is confirmed for "
"05-Jun-2026 at 2:00 PM. "
"Patient ID: 9.'"

    )
}

]

# =========================

# Tool Definitions

# =========================

tools = [


{
    "type": "function",
    "function": {
        "name": "get_doctor_by_department",
        "description": "Find doctor by department",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string"
                }
            },
            "required": ["department"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "check_doctor_exists",
        "description": "Find doctor by name",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {
                    "type": "string"
                }
            },
            "required": ["doctor_name"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_patient_by_phone",
        "description": "Find patient using phone number",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string"
                }
            },
            "required": ["phone_number"]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "get_available_slots",
        "description": "Get available appointment slots",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "integer"
                },
                "appointment_date": {
                    "type": "string"
                }
            },
            "required": [
                "doctor_id",
                "appointment_date"
            ]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "is_slot_available",
        "description": "Check whether a slot is available",
        "parameters": {
            "type": "object",
            "properties": {

                "doctor_id": {
                    "type": "integer"
                },

                "appointment_date": {
                    "type": "string"
                },

                "appointment_time": {
                    "type": "string"
                }
            },

            "required": [
                "doctor_id",
                "appointment_date",
                "appointment_time"
            ]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "create_patient",
        "description": "Register a new patient",
        "parameters": {
            "type": "object",
            "properties": {

                "first_name": {
                    "type": "string"
                },

                "last_name": {
                    "type": "string"
                },

                "email": {
                    "type": "string"
                },

                "phone_number": {
                    "type": "string"
                },

                "city": {
                    "type": "string"
                }
            },

            "required": [
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "city"
            ]
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "book_appointment",
        "description": "Book appointment for patient",
        "parameters": {
            "type": "object",
            "properties": {

                "patient_id": {
                    "type": "integer"
                },

                "doctor_id": {
                    "type": "integer"
                },

                "appointment_date": {
                    "type": "string"
                },

                "appointment_time": {
                    "type": "string"
                },

                "symptoms": {
                    "type": "string"
                }
            },

            "required": [
                "patient_id",
                "doctor_id",
                "appointment_date",
                "appointment_time",
                "symptoms"
            ]
        }
    }
}
]


# =========================

# Chatbot Loop

# =========================

while True:

    user_input = input("You: ")
    # Exit chatbot
    if user_input.lower() == "exit":

        print("\nShini: Thank you for choosing Super Clinic.")
        print("Shini: Have a wonderful day!")

        break

    # Save user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    try:

        # =========================
        # First AI Response
        # =========================

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # =========================
        # TOOL CALLING
        # =========================

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                function_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                tool_result = ""

                # =========================
                # get_doctor_by_department
                # =========================

                if function_name == "get_doctor_by_department":

                    result = get_doctor_by_department(
                        arguments["department"]
                    )

                    if result:

                        tool_result = (
                            f"Doctor ID: {result.DoctorID}, "
                            f"Name: {result.FirstName} "
                            f"{result.LastName}, "
                            f"Department: {result.Department}"
                        )

                    else:

                        tool_result = "No doctor found."

                # =========================
                # check_doctor_exists
                # =========================

                elif function_name == "check_doctor_exists":

                    result = check_doctor_exists(
                        arguments["doctor_name"]
                    )

                    if result:

                        tool_result = (
                            f"Doctor ID: {result.DoctorID}, "
                            f"Name: {result.FirstName} "
                            f"{result.LastName}, "
                            f"Department: {result.Department}"
                        )

                    else:

                        tool_result = "Doctor not found."

                # =========================
                # get_patient_by_phone
                # =========================

                elif function_name == "get_patient_by_phone":

                    result = get_patient_by_phone(
                        arguments["phone_number"]
                    )

                    if result:

                        tool_result = (
                            f"Patient ID: {result.PatientID}, "
                            f"Name: {result.FirstName} "
                            f"{result.LastName}"
                        )

                    else:

                        tool_result = "Patient not found."

                # =========================
                # get_available_slots
                # =========================

                elif function_name == "get_available_slots":

                    result = get_available_slots(
                        arguments["doctor_id"],
                        arguments["appointment_date"]
                    )

                    if result:

                        tool_result = (
                            "Available Slots: "
                            + ", ".join(result)
                        )

                    else:

                        tool_result = "No slots available."
                # =========================
                # is_slot_available
                # =========================

                elif function_name == "is_slot_available":

                    result = is_slot_available(
                            arguments["doctor_id"],
                            arguments["appointment_date"],
                            arguments["appointment_time"]
                        )

                    if result:

                        tool_result = (
                            "Selected slot is available."
                        )

                    else:

                        tool_result = (
                            "Selected slot is already booked."
                        )
                # =========================
                # create_patient
                # =========================

                elif function_name == "create_patient":

                    result = create_patient(
                            arguments["first_name"],
                            arguments["last_name"],
                            arguments["email"],
                            arguments["phone_number"],
                            arguments["city"]
                        )

                    if result:

                        tool_result = (
                            f"Patient registered successfully. "
                            f"Patient ID: {result}"
                        )

                    else:

                         tool_result = (
                            "Patient registration failed."
                         )
                # =========================
                # book_appointment
                # =========================

                elif function_name == "book_appointment":

                    result = book_appointment(
                             arguments["patient_id"],
                             arguments["doctor_id"],
                             arguments["appointment_date"],
                             arguments["appointment_time"],
                             arguments["symptoms"]
                    )

                    tool_result = result
                # =========================
                # Unknown Tool
                # =========================

                else:

                    tool_result = "Tool execution failed."

                # Save tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

            # =========================
            # SECOND AI RESPONSE
            # =========================

            second_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )

            final_reply = (
                second_response
                .choices[0]
                .message
                .content
            )

            print(f"Shini: {final_reply}")

            messages.append({
                "role": "assistant",
                "content": final_reply
            })

        # =========================
        # NORMAL RESPONSE
        # =========================

        else:

            bot_reply = message.content

            print(f"Shini: {bot_reply}")

            messages.append({
                "role": "assistant",
                "content": bot_reply
            })

    except Exception as e:

        print("\nShini: Sorry, an error occurred.")
        print("Error:", e)

