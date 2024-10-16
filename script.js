const generateForm = document.querySelector(".generate-form");
const generateBtn = generateForm.querySelector(".generate-btn");
const imageGallery = document.querySelector(".image-gallery");

const headers = {
  'Content-Type': 'application/json',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.1',
  'Accept': '*/*',
};

let isImageGenerating = false;

// Function to update image card with the generated image
const updateImageCard = (imgObject) => {
  const imgCard = imageGallery.querySelector(".img-card");
  const imgElement = imgCard.querySelector("img");
  const downloadBtn = imgCard.querySelector(".download-btn");

  const aiGeneratedImage = `data:image/jpeg;base64,${imgObject.photo}`; // Update to match your API response structure
  imgElement.src = aiGeneratedImage;

  imgElement.onload = () => {
    imgCard.classList.remove("loading");
    downloadBtn.setAttribute("href", aiGeneratedImage);
    downloadBtn.setAttribute("download", `${new Date().getTime()}.jpg`);
  };
};

// Function to generate AI image
const generateAiImage = async (userPrompt) => {
  try {
    const data = { prompt: userPrompt }; // Request 1 image
    const response = await fetch('https://own-ai.onrender.com/api/v1/generateImage', {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    const responseJson = await response.json();

    // Log the response for debugging
    console.log("API Response Status:", response.status);
    console.log("API Response JSON:", responseJson);

    // Check for expected image data in the response
    if (response.status === 200 && responseJson.data && responseJson.data.photo) {
      updateImageCard(responseJson.data); // Update the image card with the returned image
    } else {
      throw new Error("API response did not contain the expected image data.");
    }
  } catch (error) {
    console.error("Error generating image:", error);
    alert(error.message);
  } finally {
    generateBtn.removeAttribute("disabled");
    generateBtn.innerText = "Generate";
    isImageGenerating = false;
  }
};

// Handle form submission to generate image
const handleImageGeneration = (e) => {
  e.preventDefault();
  if (isImageGenerating) return;

  const userPrompt = e.srcElement[0].value;

  // Disable the generate button and show loading state
  generateBtn.setAttribute("disabled", true);
  generateBtn.innerText = "Generating...";
  isImageGenerating = true;

  // Create HTML markup for a single image card with loading state
  const imgCardMarkup = `
      <div class="img-card loading"> 
        <img src="images/loader.svg" alt="Loading..."> 
        <a class="download-btn" href="#"> 
          <img src="images/download.svg" alt="Download icon"> 
        </a> 
      </div>
  `;

  imageGallery.innerHTML = imgCardMarkup; // Clear previous images and show loading
  generateAiImage(userPrompt); // Call function to generate image
};

// Add event listener to the form
generateForm.addEventListener("submit", handleImageGeneration);
