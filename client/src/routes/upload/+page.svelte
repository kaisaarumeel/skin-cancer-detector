<script lang="ts">
  import TopBar from "../../components/TopBar.svelte";
  import Guide from "../../components/Guide.svelte";
  import { goto } from '$app/navigation';
  import { routeGuard } from '../../routeGuard';  // Import the route guard
  import { onMount } from "svelte";
  import { API } from '../../api'; // Import the API instance

  // Check if the user is logged in when the page is loaded
  onMount(() => {
    routeGuard();
  });
    
  // Track the current step and visibility of the guide
  let currentStep = 1;
  const totalSteps = 5; // Updated to match the number of steps in Guide
  
  // Function to handle advancing steps
  function nextStep() {
    if (currentStep < totalSteps) {
      currentStep++; // Increment currentStep
    }
  }

  let selectedFile: File | null = null;
  let fileName = "No file chosen";
  let localization = ""

  let fileError = ""
  let localizationError = ""

  // Updated function with TypeScript type annotation
  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement; // Type assertion
    selectedFile  = input.files?.[0] || null ; // Use optional chaining
    if (selectedFile) {
      fileName = selectedFile.name;
    } else {
      fileName = "No file chosen";
    }
  }
   
  async function handleAnalyze(event: Event)
  {
    if (!selectedFile) {
      console.error("No file selected");
      fileError = "No file is selected."
      return; 
    }
    if (!localization) {
      console.error("No localization selected")
      localizationError = "No localization is selected."
      return; 
    }
    try{
      const base64Image = await fileToBase64(selectedFile); // convert image to the base 64 format
      const response = await API.post('/api/create-request/', {
        "localization": localization,
        "image": base64Image
      });

      if(response.status == 201)
      {
        // TODO: Add get results endpoint/logic here
        goto('/results');
      }
    }
    catch(err){
      console.error(err)
    }
  }

  // Function to change the submitted 
  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => {
        const result = reader.result;
        if (typeof result === "string") {
          // Removes the Base64 header
          resolve(result.split(",")[1]);
        } else {
          reject(new Error("Unexpected result type from FileReader"));
        }
      };

      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file); // Reads the file as a Base64 encoded string
    });
  }

</script>

<div class="h-screen flex flex-col relative">
  <TopBar></TopBar>

  <!-- Guide Component as an Overlay -->
  {#if currentStep < totalSteps}
    <div class="backdrop-blur-sm absolute top-0 left-0 w-full h-full bg-opacity-50 flex items-center justify-center">
      <Guide {currentStep} on:nextStep={nextStep}></Guide>
    </div>
  {/if}

  <div class="h-full w-full flex items-center justify-center">
    <div class="flex flex-col items-center justify-center lg:w-6/12 w-10/12">
      <h1 class="text-secondary text-3xl font-extralight mb-20">Upload a photo of your skin</h1>
      <p class="text-tertiary mb-2">For a more precise analysis choose the body part where the mole is located.</p>

      {#if localizationError}
        <p class="text-red-500 mb-2">{localizationError}</p>
      {/if}

      <div class="mb-4 w-full">
        <select bind:value={localization} class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" aria-label="Body Part">
          <option value="" disabled selected class="text-gray-400">Select Body Part</option>
          <option value="ear">Ear</option>
          <option value="face">Face</option>
          <option value="neck">Neck</option>
          <option value="scalp">Scalp</option>
        
          <optgroup label="Trunk region">
            <option value="abdomen">Abdomen</option>
            <option value="back">Back</option>
            <option value="chest">Chest</option>
            <option value="trunk">Trunk - Other</option>
          </optgroup>
        
          <optgroup label="Upper limbs">
            <option value="acral">Acral (Fingers/Toes)</option>
            <option value="hand">Hand</option>
            <option value="upper_extremity">Upper Extremity (Arm)</option>
          </optgroup>
        
          <optgroup label="Lower limbs">
            <option value="foot">Foot</option>
            <option value="lower_extremity">Lower Extremity (Leg)</option>
          </optgroup>
        
          <option value="genital">Genital Area</option>
        </select>
      </div>

      <form class="mt-10 w-full">
        <div class="flex items-center bg-slate-50 shadow-md p-3 rounded-lg justify-between">
          <label for="fileInput" class="p-2 border-tertiary border rounded-2xl flex items-center text-tertiary font-light cursor-pointer mr-4 hover:bg-stone-200">
            <img src="upload-file.png" alt="Upload a File" class="h-5 mr-4">
            Upload File
          </label>
      
          <input
            id="fileInput"
            type="file"
            class="hidden"
            on:change={handleFileChange}
          />
          
          <span class="text-tertiary">{fileName}</span>
        </div>
      </form>
      {#if fileError}
        <p class="text-red-500 mb-2">{fileError}</p>
      {/if}
      <button on:click={handleAnalyze} class="w-1/2 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-10 hover:bg-secondary shadow-l">Analyze</button>
    </div>
  </div>
</div>
