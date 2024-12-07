<script lang="ts">
    import TopBar from "../../components/TopBar.svelte";
    import { goto } from '$app/navigation';
    import { API } from '../../api'; 
    import { onMount, onDestroy } from "svelte";
    import { routeGuard } from "../../routeGuard";
    import FeatureImpact from "../../components/FeatureImpact.svelte"; 


    interface ScanHistory {
      id: number;
      date: string;
      bodyPart: string;
      image: string;
      prediction: string;
      probability: number; 
    }
    
    let expandedScanId: number | null = null;
    let scanHistory: ScanHistory[] = [];
    let error: string | null = null;
    
    async function fetchScanHistory() {
      error = null;
      try {
          const response = await API.get('/api/get-requests-by-username');
          scanHistory = response.data.requests.map((req: any) => ({
              id: req.request_id,
              date: formatDate(req.created_at),
              bodyPart: req.localization,
              image: `data:image/jpeg;base64,${req.image}`,
              prediction: req.lesion_type || "Pending...",
              probability: req.probability, 
          }));

      } catch (err: unknown) {
          if (err instanceof Error) {
              error = err.message;
          } else {
              error = 'An unknown error occurred.';
          }
      } 
    }
  
    // Function to format the timestamp to a human-readable format
    function formatDate(timestamp: number): string {
      // Convert from seconds to milliseconds
      const date = new Date(timestamp * 1000); 
      // Format the date
      return date.toLocaleDateString('en-UK', {
        year: 'numeric',
        month: 'short',  
        day: 'numeric',  
        hour: '2-digit',
        minute: '2-digit' 
      });
    }
  
    function toggleExpandScan(scanId: number): void {
      expandedScanId = expandedScanId === scanId ? null : scanId;
    }
  
    function newScan() {
      goto('/upload');
    }
    
    // Fetch scan history on mount and set interval for periodic updates
    let intervalId: ReturnType<typeof setInterval>;
  
    onMount(() => {
      routeGuard();
      fetchScanHistory();  // Initial fetch
      intervalId = setInterval(fetchScanHistory, 5000);  // Fetch every 5 seconds
    });
  
    // Cleanup interval when the component is destroyed
    onDestroy(() => {
      clearInterval(intervalId);  // Clear interval on component destroy
    });
  </script>
  
  <div class="h-screen flex flex-col">
    <div class="flex-shrink-0">
      <TopBar />
    </div>
    <div class="flex-1 w-full p-4 sm:p-6 flex flex-col items-center overflow-y-auto">
      <h1 class="text-secondary text-xl sm:text-2xl font-extralight mb-4">Scan History</h1>
  
      {#if error}
        <p class="text-red-500">Error: {error}</p>
      {:else if scanHistory.length > 0}
        <div class="overflow-x-auto w-full">
          <table class="min-w-full">
            <thead class="bg-primary text-white rounded-t-lg">
              <tr>
                <th class="border-b border-gray-200 p-3 sm:p-4 text-left font-light">Date</th>
                <th class="border-b border-gray-200 p-3 sm:p-4 text-left font-light">Body Part</th>
                <th class="border-b border-gray-200 p-3 sm:p-4 text-left font-light">Predicted Lesion Type</th>
                <th class="border-b border-gray-200 p-3 sm:p-4 text-left font-light">Probability</th> <!-- New column for Probability -->
                <th class="border-b border-gray-200 p-3 sm:p-4 text-center font-light">Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each scanHistory as scan (scan.id)}
                <tr class="even:bg-gray-50 odd:bg-white hover:bg-gray-100 transition-colors">
                  <td class="border-b border-gray-200 p-3 sm:p-4 text-tertiary text-sm sm:text-base">{scan.date}</td>
                  <td class="border-b border-gray-200 p-3 sm:p-4 text-tertiary text-sm sm:text-base">{scan.bodyPart}</td>
                  <td class="border-b border-gray-200 p-3 sm:p-4 text-tertiary text-sm sm:text-base">{scan.prediction}</td>
                  <td class="border-b border-gray-200 p-3 sm:p-4 text-tertiary text-sm sm:text-base">{scan.probability ? (scan.probability * 100).toFixed(2) + '%' : 'N/A'}</td> <!-- Display probability -->
                  <td class="border-b border-gray-200 p-3 sm:p-4 text-center">
                    <button
                      type="button"
                      class="px-4 py-2 bg-primary text-white font-light rounded-lg hover:bg-secondary transition"
                      on:click={() => toggleExpandScan(scan.id)}
                    >
                      {expandedScanId === scan.id ? "Collapse" : "Expand"}
                    </button>
                  </td>
                </tr>
                {#if expandedScanId === scan.id}
                  <tr>
                    <td colspan="5" class="border-b p-6 bg-gray-100">
                      <div class="flex flex-col lg:flex-row items-center gap-6">
                        <div>
                          <img
                          src="{scan.image}"
                          alt="Skin scan"
                          class="h-40 w-40 object-cover border"
                        />
                        <div class="mt-2">
                          <FeatureImpact scan={scan.id}/>

                        </div>

                        </div>
                        <div class="flex-1">
                          <p class="text-lg text-tertiary font-medium">Scan Details</p>
                          <div class="mt-4 space-y-2">
                            <p class="text-tertiary font-light"><strong>Created at:</strong> {scan.date}</p>
                            <p class="text-tertiary font-light"><strong>Body Part:</strong> {scan.bodyPart}</p>
                            <p class="text-tertiary font-light"><strong>Prediction:</strong> {scan.prediction}</p>
                            <p class="text-tertiary font-light"><strong>Probability of the result:</strong> {scan.probability ? (scan.probability * 100).toFixed(2) + '%' : 'N/A'}</p> 
                          </div>
                        </div>
                       
                      </div>
                    </td>
                  </tr>
                {/if}
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <p class="text-tertiary mt-10">You have no scans yet. Start by uploading an image of your skin for analysis.</p>
      {/if}
  
      <button
        on:click={newScan}
        class="w-2/3 lg:w-1/3 p-3 bg-primary text-white font-light rounded-lg cursor-pointer mt-10 hover:bg-secondary shadow-md"
      >
        Scan a New Image
      </button>
    </div>
  </div>
  