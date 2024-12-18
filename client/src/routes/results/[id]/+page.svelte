<script lang="ts">
  import { page } from '$app/stores';
  import { onMount, onDestroy } from "svelte";
  import { API } from "../../../api";
  import { routeGuard } from "../../../routeGuard";
  import { goto } from "$app/navigation";
  import TopBar from "../../../components/TopBar.svelte";
  import FeatureImpact from '../../../components/FeatureImpact.svelte';
  import { isAxiosError } from "axios";

  interface RequestData {
    request_id: number;
    image: string;
    probability: number | null;
    lesion_type: string | null;
  }

  const MALIGNANT_LESION_TYPES = ["Melanoma (Malignant)", "Basal cell carcinoma (Malignant)", "Actinic keratoses and intraepithelial carcinoma (Malignant)"]; // Malignant lesion types
  let requestId: string = $page.params.id;
  let requestData: RequestData | null = null;
  let errorMessage: string | null = null;
  let intervalId: ReturnType<typeof setInterval> | null = null;
  let showModal: boolean = false; // Controls modal visibility

  // Function to check if the lesion type is malignant
  function isMalignant(lesionType: string | null): boolean {
    return lesionType !== null && MALIGNANT_LESION_TYPES.includes(lesionType);
  }

  async function fetchData() {
    try {
      const response = await API.get(`/api/get-specific-request/${requestId}/`);
      if (response.status === 200) {
        const data = response.data.request;
        requestData = {
          ...data,
          image: `data:image/jpeg;base64,${data.image}`, // Convert to Base64
        } as RequestData;
        errorMessage = null; // Clear any previous errors

        // Stop fetching if lesion_type and probability are not null
        if (requestData.lesion_type !== null && requestData.probability !== null) {
          clearInterval(intervalId!);
          intervalId = null;
        }
      }
    } catch (err) {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
      if (isAxiosError(err)) {
        // Safely access the data field and assert its type
        const errorResponse = err.response?.data as { err?: string } | undefined;
        // Check if the "err" property exists and is a string
        if (typeof errorResponse?.err === "string") {
          // Use it as error message
          errorMessage = errorResponse.err;
        } else {
          errorMessage = "An unexpected error occurred while fetching data.";
        }
        showModal = true; // Show the modal
      }
    }
  }

  onMount(() => {
    routeGuard();
    // Initial fetch
    fetchData();

    // Set up interval to fetch data every 2 seconds if necessary
    if (!requestData || requestData.lesion_type === null || requestData.probability === null) {
      intervalId = setInterval(fetchData, 2000);
    }

    // Cleanup interval on component destroy
    onDestroy(() => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    });
  });

  function closeModalAndRedirect() {
    showModal = false;
    goto("/upload");
  }
</script>

<div class="h-screen flex flex-col">
  <div class="flex-shrink-0">
    <TopBar />
  </div>
  <div class="w-full p-4 flex flex-col items-center justify-center">
    <h1 class="text-secondary text-xl sm:text-2xl font-extralight mb-4">Scan Result</h1>
    {#if errorMessage && !showModal}
      <p class="text-red-500">{errorMessage}</p>
    {:else if !requestData || requestData.lesion_type === null || requestData.probability === null}
      {#if !showModal}
        <div class="flex flex-col items-center mt-20">
          <p class="text-tertiary mb-10">Loading...</p>
          <div class="spinner"></div> 
        </div>
      {/if}
    {:else}
      <div class="flex flex-col lg:flex-row items-center mt-10 lg:items-center lg:justify-center w-full p-4">
        <!-- Image Section -->
        <div class="lg:w-1/3 mb-10 mr-2 flex justify-center">
          <!-- svelte-ignore a11y_img_redundant_alt -->
          <img 
            src={requestData.image} 
            alt="Uploaded Image" 
            class="w-60 h-60 lg:w-80 lg:h-80 object-cover border rounded shadow-md"
          />
        </div>
        
        <!-- Information Section -->
        <div class="lg:w-2/3 flex flex-col">

          <div class="p-8 bg-slate-50 flex items-center justify-center shadow-lg rounded-lg">
            Model's prediction:&nbsp;
            <span class="font-bold">{(requestData.probability * 100).toFixed(2)}% likelihood of being {requestData.lesion_type}</span>.
          </div>
          {#if isMalignant(requestData.lesion_type)}
            <p class="text-tertiary mt-6 ">
              With this prediction, we advise you to visit a doctor for a medical checkup on your skin.
            </p>
          {/if}
          <div class="mt-6 flex flex-col lg:items-start items-center">
            <p class="text-sm text-tertiary mb-2">How did the model predict this?</p>
            <FeatureImpact scan={requestData.request_id}/>
          </div>
          <div class="mt-10 w-full flex justify-center">
            <button 
              on:click={() => goto("/upload")} 
              class="w-full w-full lg:w-1/2 px-6 py-3 bg-primary text-white font-light rounded-md cursor-pointer transition-colors hover:bg-secondary shadow-md"
            >
              Scan Another Mole
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Modal -->
  {#if showModal}
    <div class="modal-overlay">
      <div class="modal-content">
        <h2 class="modal-title">Error</h2>
        <p class="modal-message">{errorMessage}</p>
        <div class="modal-actions">
          <button class="button-primary" on:click={closeModalAndRedirect}>Try Again</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .spinner {
    border: 4px solid #f3f3f3; 
    border-top: 4px solid #B7A9D4;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1.5s linear infinite;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }

  .modal-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    width: 90%;
    max-width: 400px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .modal-title {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #333;
  }

  .modal-message {
    font-size: 1rem;
    margin-bottom: 1.5rem;
    color: #EF4444;
  }

  .modal-actions .button-primary {
    background-color: #6b46c1;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .modal-actions .button-primary:hover {
    background-color: #805ad5;
  }
</style>
