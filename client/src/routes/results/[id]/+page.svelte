<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from "svelte";
  import { API } from "../../../api";
  import { routeGuard } from "../../../routeGuard";
  import { goto } from "$app/navigation";
  import TopBar from "../../../components/TopBar.svelte";

  // Define types for request data
  interface RequestData {
    request_id: string;
    created_at: string;
    image: string;
    probability: number;
    localization: string;
    lesion_type: string;
    user: string;
    model_version?: string | null;
    feature_impact: { feature: string; impact: number }[];
  }

  let requestId: string = $page.params.id; // Use $page.params to get the ID
  let requestData: RequestData | null = null;
  let error: string | null = null;

  onMount(async () => {
    routeGuard();

    try {
      const response = await API.get(`/api/get-specific-request/${requestId}/`);
      if (response.status === 200) {
        requestData = response.data.request as RequestData;
        console.log(requestData)
      } else {
        error = "Failed to fetch request data.";
      }
    } catch (err) {
      console.error(err);
      error = "An error occurred while fetching request data.";
    }
  });
</script>

<div class="h-screen flex flex-col relative">
  <TopBar></TopBar>

  <div class="h-full w-full p-10 flex flex-col items-center justify-center">
    {#if error}
      <p class="text-red-500">{error}</p>
    {:else if !requestData}
      <p>Loading...</p>
    {:else}
      <h1 class="text-secondary text-3xl font-extralight mb-20">Results</h1>
      <p class="text-tertiary mb-10">Based on your uploaded image, it is likely that your mole is {requestData.lesion_type}.</p>
      <div class="p-8 h-20 bg-slate-50 flex items-center justify-center shadow-lg">
        Model's prediction: {Math.round(requestData.probability * 100)}% {requestData.lesion_type}.
      </div>
      <p class="text-tertiary mt-10">With this prediction rate, we advise you to visit a doctor for a medical checkup on your mole.</p>
      <p class="text-tertiary text-sm font-extralight mt-10">Do you want to scan another mole?</p>
      <button on:click={() => goto("/upload")} class="w-1/2 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-1 transition-colors hover:bg-secondary shadow-l">
        Another scan
      </button>
    {/if}
  </div>
</div>
