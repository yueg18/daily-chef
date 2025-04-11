import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from PIL import Image
import openai
from openai import OpenAI


# Function to set a background image and black banner
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/alikassi/kitchen_image.jpg/main/kitchen_image.jpg");
            background-size: cover;
        }}
        .stTitleBanner {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black banner */
            padding: 40px;  /* Increase padding to accommodate subtext */
            border-radius: 0 0 10px 10px;  /* Add rounded corners to the bottom */
        }}
        .stTitleBox {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black box */
            padding: 20px;  /* Increase padding */
            border-radius: 10px;  /* Add rounded corners */
            margin-bottom: 20px;  /* Add margin below the box */
            color: white;  /* Set text color to white */
        }}
        .stText {{
            color: white;  /* Set subtext color to white */
            font-size: large;  /* Adjust subtext font size */
        }}
        .review-button {{
            cursor: pointer;
            color: blue;
            background-color: rgba(0, 0, 0, 0.5);  /* Semi-transparent black button */
            padding: 10px 20px;  /* Add padding to the button */
            border-radius: 5px;  /* Add rounded corners */
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.4);  /* Semi-transparent black overlay */
            padding-top: 60px;
        }}
        .modal-content {{
            background-color: rgba(0, 0, 0, 0.8);  /* Semi-transparent black box */
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
            color: white;  /* Set text color to white */
        }}
        .form-text {{
            background-color: rgba(255, 255, 255, 0.1);  /* Semi-transparent white text box */
            color: white;  /* Set text color to white */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function for Home Page

# Function for Home Page
def display_image_popup(image_filenames, visibility, key):
    # Display the additional images based on the selected main image
    if visibility[key]:
        for img_filename in image_filenames:
            if img_filename.endswith('_r.png') or img_filename.endswith('_NF.jpeg'):
                st.image(img_filename, width=500)  # Adjust width as needed
            elif img_filename.endswith('_ins.png'):
                st.image(img_filename, width=500)  # Adjust width as needed
def home_page():
    # Titles and main images
    titles = ["Vegetarian Recipe", "Gluten-Free Dessert", "Diabetes Friendly"]
    main_images = ["Veg.jpeg", "CC.jpeg", "DM.jpeg"]
    
    # Additional images for each category
    additional_images = {
        "Vegetarian Recipe": ["veg_r.png", "veg_ins.png"],
        "Gluten-Free Dessert": ["GF_r.png", "GF_ins.png"],
        "Diabetes Friendly": ["DM_r.png", "DM_ins.png"]
    }
    nutritional_images = {
        "Vegetarian Recipe": ["veg_NF.jpeg"],
        "Gluten-Free Dessert": ["GF_NF.jpeg"],
        "Diabetes Friendly": ["DM_NF.jpeg"]
    }

    # Define initial visibility states for each additional image
    recipe_visibility = {title: False for title in titles}
    nutritional_visibility = {title: False for title in titles}

    st.markdown('<div class="stTitleBanner"><h1 class="stTitle">SnapSupper</h1><p class="stText">Welcome to SnapSupper! Upload a photo of your fridge on the "Recipe Generator" page to get started.</p></div>', unsafe_allow_html=True)
    # Inject custom CSS styles for the titles
    st.markdown("""
        <style>
        .image-title {
            font-weight: bold;
            font-size: 18px; /* Adjust font size as needed */
            color: #ffffff; /* White text color */
            background-color: rgba(0,0,0,0.5); /* Semi-transparent black background */
            padding: 5px;
            border-radius: 5px; /* Rounded corners */
            text-align: center; /* Center-align text */
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for col, title, main_img in zip(cols, titles, main_images):
        with col:
            st.markdown(f"<div class='image-title'>{title}</div>", unsafe_allow_html=True)
            st.image(main_img, width=300)  # Display the main image
            button_clicked = False
            if st.button('Recipe', key=f"{title}_recipe"):
                button_clicked = True
                # Toggle recipe visibility when the recipe button is clicked
                recipe_visibility[title] = not recipe_visibility[title]
            if st.button('Nutritional Facts', key=f"{title}_nutrition"):
                button_clicked = True
                # Toggle nutritional visibility when the nutritional button is clicked
                nutritional_visibility[title] = not nutritional_visibility[title]
            # If no button is clicked, display nutritional images by default
            if not button_clicked:
                display_image_popup(nutritional_images[title], nutritional_visibility, title)
            # Display images based on visibility flags
            if recipe_visibility[title]:
                display_image_popup(additional_images[title], recipe_visibility, title)
            elif nutritional_visibility[title]:
                display_image_popup(nutritional_images[title], nutritional_visibility, title)



prompt = "What are ingredients in this fridge? And can you create recipes from it"




def recipe_generator():
    st.title("💬 Recipe Generator")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI LLM")
   
    # Sidebar for OpenAI API Key input
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key_1", type="password")
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
        
    # Initialize conversation history in session state
    if 'conversation_history' not in st.session_state:
        st.session_state['conversation_history'] = []

    # Display conversation history
    for message in st.session_state['conversation_history']:
        if message['role'] == "user":
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # File uploader for image
    uploaded_image = st.file_uploader("Upload Image (Optional)", type=["jpg", "png", "jpeg"])

    # Text input and send button
    user_input_text = st.text_input("Enter your message", key="user_message", on_change=None)
    send_button = st.button("Send")

    # Process uploaded image
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        image_filename = "uploaded_image.jpg"
        image.save(image_filename)

        image_url = "https://media.istockphoto.com/id/842160124/photo/refrigerator-with-fruits-and-vegetables.jpg?s=612x612&w=0&k=20&c=j0W4TPOevBpp3mS6_X2FHV1uWVl3fcfdGAt2X3l8XzE="  # Placeholder URL
        st.session_state['conversation_history'].append({"role": "user", "content": image_url})
        
    # Dietary preferences
    st.header("Dietary Preferences")
    dietary_preferences_options = [
        "Lactose intolerance",
        "Gluten intolerance or sensitivity",
        "Vegetarianism",
        "Veganism",
        "Kosher",
        "Keto",
        "Diabetes",
        "Dairy-free"
    ]
    dietary_preferences_selected = st.multiselect("Select dietary preferences", dietary_preferences_options)

    # Other dietary preferences
    other_dietary_preference = st.checkbox("Other (please specify)", key="other_dietary_preference_checkbox")
    if other_dietary_preference:
        other_dietary_preference_text = st.text_input("Other dietary preferences", key="other_dietary_preference_text")

    # Allergies
    st.header("Allergies")
    allergies_options = [
        "Milk",
        "Eggs",
        "Fish",
        "Crustacean shellfish",
        "Tree nuts",
        "Peanuts",
        "Wheat",
        "Soybeans"
    ]
    allergies_selected = st.multiselect("Select allergies", allergies_options)

    # Other allergies
    other_allergies = st.checkbox("Other (please specify)", key="other_allergies_checkbox")
    if other_allergies:
        other_allergies_text = st.text_input("Other allergies", key="other_allergies_text")

    # Process user input and generate response
    if send_button:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        
        if user_input_text.strip():  
            st.session_state['conversation_history'].append({"role": "user", "content": user_input_text})
        if uploaded_image is not None:
            st.session_state['conversation_history'].append({"role": "user", "content": image_url})

        client = OpenAI(api_key=openai_api_key)
        
        user_message = user_input_text
        if dietary_preferences_selected:
            user_message += "\n\nDietary Preferences: "
            user_message += ", ".join(dietary_preferences_selected)
            if other_dietary_preference and other_dietary_preference_text:
                user_message += f", {other_dietary_preference_text}"
        
        if allergies_selected:
            user_message += "\n\nAllergies: "
            user_message += ", ".join(allergies_selected)
            if other_allergies and other_allergies_text:
                user_message += f", {other_allergies_text}"
       
        messages = []
        if uploaded_image is not None:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {"type": "image_url", "image_url": image_url},
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": user_message}]
            })

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )

        assistant_response = response.choices[0].message.content
        st.session_state['conversation_history'].append({"role": "assistant", "content": assistant_response})
        
        st.chat_message("user").write(user_message)
        st.chat_message("assistant").write(assistant_response)




def about_page():
    st.markdown('<div class="stTitleBanner"><h1 class="stTitle">About SnapSupper</h1><p class="stText">Daily Chef Meal Planner aims to revolutionize meal planning by developing one AI system that suggests recipes based on the contents of a user\'s fridge, dietary preferences, and nutritional goals. This innovative application promises to reduce food waste, enhance dietary variety, and support nutritional goals through personalized culinary suggestions. It features ingredient recognition, recipe customization, and user feedback integration to refine and personalize meal recommendations.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="stTitleBox"><h2 class="stTitle">Founders</h2><p class="stText">Meet the founders of SnapSupper:</p></div>', unsafe_allow_html=True)

    # Custom CSS for captions
    st.markdown("""
    <style>
    .caption {
        font-weight: bold;
        font-size: 16px; /* Increase font size */
        color: #ffffff; /* White text color, change as needed */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        text-align: center; /* Center-align text */
    }

    .faq-question {
        font-weight: bold;
        font-size: 18px;
        color: #ffffff; /* White text color */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        margin-bottom: 10px;
    }

    .faq-answer {
        font-size: 16px;
        color: #ffffff; /* White text color */
        background-color: rgba(0,0,0,0.6); /* Semi-transparent black background for contrast */
        padding: 3px;
        border-radius: 5px; /* Rounded corners for the caption background */
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    image_filenames = ["alik.jpg", "Sne.jpg", "Yue.jpg", "Mic.jpg", "Sid.jpg"]
    captions = ["Alik Assi", "Sneha Sahu", "Yue Guo", "Michael Carter", "Sidra Imran"]

    cols = st.columns(5)
    for col, img_filename, caption in zip(cols, image_filenames, captions):
        with col:
            st.image(img_filename, width=100, output_format='JPEG', use_column_width=False)
            # Wrap the caption in a div with the class 'caption' for styling
            st.markdown(f"<div class='caption'>{caption}</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="stTitleBox"><h2 class="stTitle">FAQ</h2></div>', unsafe_allow_html=True)

    # Define frequently asked questions and their answers
    faqs = [
        {"question": "1. What is SnapSupper?", "answer": "SnapSupper is a Daily Chef Meal Planner that uses AI to suggest recipes based on the contents of your fridge, dietary preferences, and nutritional goals."},
        {"question": "2. How does SnapSupper work?", "answer": "SnapSupper analyzes the ingredients in your fridge, along with your dietary preferences and nutritional goals, to generate personalized recipe recommendations."},
        {"question": "3. Who are the founders of SnapSupper?", "answer": "SnapSupper was founded by Alik Assi, Sneha Sahu, Yue Guo, Michael Carter, and Sidra Imran."},
        # Add more questions and answers as needed
    ]

    # Display FAQs with improved styling
    for faq in faqs:
        st.markdown(f"<p class='faq-question'>{faq['question']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='faq-answer'>{faq['answer']}</p>", unsafe_allow_html=True)


def review_section():
    st.markdown('<div class="stTitleBox"><h2 class="stTitle">Reviews</h2></div>', unsafe_allow_html=True)
    
    st.write("### Rate your experience")
    
    # Text input for the reviewer's name
    user_name = st.text_input("Your name", key='user_name')
    
    # Use a slider for rating
    user_rating = st.slider("Select your rating", 0, 5, 1)  # Start at 1, range is from 0 to 5
    
    # Review text input
    review_text = st.text_area("Your review", height=150, key='review_text')
    
    # Initialize the reviews list in the session state if it doesn't exist
    if 'reviews' not in st.session_state:
        st.session_state['reviews'] = []
    
    # Submit button for the review
    if st.button('Submit Review'):
        # Append the new review to the session state list
        st.session_state['reviews'].append((user_name, user_rating, review_text))
        
        # Clear the form (This won't actually clear the input boxes in Streamlit. See the note below.)
        user_name = ''  # This line is for illustrative purposes and won't clear the input box.
        review_text = ''  # This won't clear the textarea.
        
    st.write('\n')

    # Display each stored review
    if st.session_state['reviews']:
      st.write("### Past Reviews")
      for review in st.session_state['reviews']:
        # Ensure each review has exactly 3 elements before unpacking
        if len(review) == 3:
            name, rating, text = review
            st.write(f"Name: {name}")
            st.write(f"Rating: {rating} stars")
            st.write(f"Review: {text}")
            st.write("---")  # Add a separator line for readability
        else:
            st.write("Review data format is incorrect.")


def main():
    # Call the function to set the background image and black banner
   

    # Navigation bar using hyperlinks
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Recipe Generator", "About", "Reviews"])

    if page == "Home":
        home_page()
        set_background()
    elif page == "Recipe Generator":
        recipe_generator()
    elif page == "About":
        about_page()
        set_background()
    elif page == "Reviews":
        review_section()
        
  
if __name__ == "__main__":
    main()
