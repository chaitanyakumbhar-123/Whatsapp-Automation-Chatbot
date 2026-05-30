from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

from twilio.twiml.messaging_response import MessagingResponse

from ai_agent import ask_ai
from database import (
    save_message,
    get_last_product,
    get_customer_state,
    save_customer_state,
    reset_customer_state
)
from products.product_catalog import PRODUCT_CATALOG

router = APIRouter()

CONTACT_NUMBERS = [
    "9175712484",
    "8421001436"
]


@router.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):

    user_number = From
    user_message = Body.lower()

    # Get customer memory
    customer_state = get_customer_state(user_number)

    if customer_state is None:
        customer_state = {
            "model_name": None,
            "size_ft": None,
            "dimension_space": None,
            "material": None,
            "uparna_color": None,
            "dotar_color": None,
            "extra_requirements": None,
            "showcase_sent": False
        }

    print("User Number:", user_number)
    print("User Message:", Body)

    # Save user message
    save_message(user_number, "user", Body)

    twilio_response = MessagingResponse()

    # -------------------------
    # MODEL SWITCH DETECTION
    # -------------------------
    available_models = [
        "dagdusheth",
        "lalbaug",
        "titwala",
        "simple"
    ]

    selected_model = None

    for model in available_models:
        if model in user_message:
            selected_model = model
            break

    # If customer changed model
    if (
        selected_model
        and customer_state["model_name"]
        and selected_model != customer_state["model_name"]
    ):

        # keep dimension space if available
        saved_dimension = customer_state["dimension_space"]

        reset_customer_state(user_number)

        customer_state = {
            "model_name": selected_model,
            "size_ft": None,
            "dimension_space": saved_dimension,
            "material": None,
            "uparna_color": None,
            "dotar_color": None,
            "extra_requirements": None,
            "showcase_sent": customer_state["showcase_sent"]
        }

        save_customer_state(
            user_number,
            model_name=selected_model,
            dimension_space=saved_dimension,
            showcase_sent=customer_state["showcase_sent"]
        )

    elif selected_model:

        customer_state["model_name"] = selected_model

        save_customer_state(
            user_number,
            model_name=selected_model,
            size_ft=customer_state["size_ft"],
            dimension_space=customer_state["dimension_space"],
            material=customer_state["material"],
            uparna_color=customer_state["uparna_color"],
            dotar_color=customer_state["dotar_color"],
            extra_requirements=customer_state["extra_requirements"],
            showcase_sent=customer_state["showcase_sent"]
        )

    # -------------------------
    # HUMAN HANDOFF
    # -------------------------
    contact_keywords = [
        "owner",
        "contact",
        "call",
        "phone",
        "person",
        "manus",
        "speak",
        "bolaycha",
        "number"
    ]

    if any(keyword in user_message for keyword in contact_keywords):

        contact_response = (
            "Nakki 😊 adhik mahitisathi ya number var sampark kara:\n\n"
            "Hanumant Kumbhar -\n"
            "📞 8421001436\n"
            "📞 9175712484"
        )

        twilio_response.message(contact_response)

        save_message(
            user_number,
            "assistant",
            contact_response
        )

        return PlainTextResponse(
        str(twilio_response),
        media_type="text/xml"
    )
    # -------------------------
    # PRICE QUESTIONS
    # -------------------------
    price_keywords = [
        "price",
        "cost",
        "rate",
        "bhav",
        "kimat"
    ]

    if any(keyword in user_message for keyword in price_keywords):

        matched_product = None

        # detect product from message
        for product_name, product_data in PRODUCT_CATALOG.items():

            for keyword in product_data["keywords"]:

                if keyword in user_message:
                    matched_product = product_name
                    break

        # if not found, use memory
        if not matched_product:
            matched_product = get_last_product(user_number)

        if matched_product:

            product_data = PRODUCT_CATALOG[matched_product]

            price_response = (
                f"{matched_product.title()} murti cha price "
                f"size ani material var depend karto 😊\n\n"
                f"{product_data['sizes']}\n"
                f"{product_data['materials']}\n\n"
                f"Tumhala konti size pahije? "
            )

        else:

            price_response = (
                "Price size ani material var depend karto 😊\n\n"
                "Tumhala konta product pahije?\n"
                "Ganpati, Laxmi ki Bail murti?"
            )

        twilio_response.message(price_response)

        save_message(
            user_number,
            "assistant",
            price_response
        )

        return PlainTextResponse(
        str(twilio_response),
        media_type="text/xml"
    )

    # -------------------------
    # PRODUCT FLOW
    # -------------------------
    for product_name, product_data in PRODUCT_CATALOG.items():

        for keyword in product_data["keywords"]:

            if keyword in user_message:
                # Save selected product in memory
                customer_state["model_name"] = product_name

                save_customer_state(
                    user_number,
                    model_name=product_name,
                    size_ft=customer_state["size_ft"],
                    dimension_space=customer_state["dimension_space"],
                    material=customer_state["material"],
                    uparna_color=customer_state["uparna_color"],
                    dotar_color=customer_state["dotar_color"],
                    extra_requirements=customer_state["extra_requirements"],
                    showcase_sent=customer_state["showcase_sent"]
                )

                product_response = (
                    f"{product_data['description']}\n\n"
                    f"He kahi photos bagha 👇"
                )

                print("Product Reply:", product_response)

                twilio_response.message(product_response)

                # Send showcase only once
                if not customer_state["showcase_sent"]:

                    for image_path in product_data["images"]:

                        image_message = twilio_response.message()

                        image_message.media(
                            f"https://whatsapp-automation-chatbot-production.up.railway.app/{image_path}"
                        )

                    # Mark showcase as sent
                    customer_state["showcase_sent"] = True

                    save_customer_state(
                        user_number,
                        model_name=customer_state["model_name"],
                        size_ft=customer_state["size_ft"],
                        dimension_space=customer_state["dimension_space"],
                        material=customer_state["material"],
                        uparna_color=customer_state["uparna_color"],
                        dotar_color=customer_state["dotar_color"],
                        extra_requirements=customer_state["extra_requirements"],
                        showcase_sent=True
                    )

                twilio_response.message(
                    f"{product_data['sizes']}\n"
                    f"{product_data['materials']}\n\n"
                    f"{product_data['followup']}"
                )

                save_message(
                    user_number,
                    "assistant",
                    product_response
                )

                return PlainTextResponse(
                str(twilio_response),
                media_type="text/xml"
            )

    # -------------------------
    # CUSTOMER STATE FLOW
    # -------------------------
    if customer_state["model_name"]:

        if customer_state["size_ft"] is None:

            customer_state["size_ft"] = Body

            save_customer_state(
                user_number,
                size_ft=Body
            )

            response = (
                "Chhan 😊\n"
                "POP ki Shadu Mati pahije?"
            )

            twilio_response.message(response)

            save_message(
                user_number,
                "assistant",
                response
            )

            return PlainTextResponse(
                str(twilio_response),
                media_type="text/xml"
            )


    # -------------------------
    # GREETING FLOW
    # -------------------------
    greeting_keywords = [
        "hi",
        "hello",
        "hey",
        "yo",
        "namaskar",
        "namaste",
        "hii",
        "kasa ahes",
        "kay mhantay"
    ]

    if any(keyword in user_message for keyword in greeting_keywords):

        greeting_response = (
            "Namaskar 😊\n\n"
            "Aamchyakade sundar koriv Ganpati, "
            "Laxmi ani Bail murti available aahet.\n\n"
            "Tumhala photo pahijet ka? "
            "Ki price / size mahiti pahije? 🙏"
        )

        twilio_response.message(greeting_response)

        save_message(
            user_number,
            "assistant",
            greeting_response
        )

        print(str(twilio_response))

        return PlainTextResponse(
            str(twilio_response),
            media_type="text/xml"
        )
    # -------------------------
    # PRODUCT UNAVAILABLE FLOW
    # -------------------------
    product_related_words = [
        "photo",
        "murti",
        "idol",
        "available",
        "aahe ka",
        "pathva",
        "show",
        "send"
    ]

    known_products = []

    for product_name, product_data in PRODUCT_CATALOG.items():

        for keyword in product_data["keywords"]:

            if keyword in user_message:
                known_products.append(product_name)

    if (
        any(word in user_message for word in product_related_words)
        and len(known_products) == 0
    ):

        unavailable_response = (
            "Maaf kara 🙏 sadhya ya product baddal mahiti nahi.\n\n"
            "Aamchyakade:\n"
            "• Ganpati murti\n"
            "• Laxmi murti\n"
            "• Bail murti\n\n"
            "available aahet 😊\n\n"
            "Tumhala kontya murti che photo pahijet?"
        )

        twilio_response.message(unavailable_response)

        save_message(
            user_number,
            "assistant",
            unavailable_response
        )

        return PlainTextResponse(
        str(twilio_response),
        media_type="text/xml"
    )
    # -------------------------
    # NORMAL AI RESPONSE
    # -------------------------
    ai_response = ask_ai(user_number, Body)

    print("AI Reply:", ai_response)

    save_message(
        user_number,
        "assistant",
        ai_response
    )

    twilio_response.message(ai_response)

    return PlainTextResponse(
        str(twilio_response),
        media_type="text/xml"
    )