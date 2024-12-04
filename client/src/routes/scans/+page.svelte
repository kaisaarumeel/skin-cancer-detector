<script lang="ts">
    import TopBar from "../../components/TopBar.svelte";
    import { goto } from '$app/navigation';
  
    interface ScanHistory {
      id: number;
      date: string;
      bodyPart: string;
      image: string; 
      prediction: string;
    }
  
    let expandedScanId: number | null = null;
  
    let scanHistory: ScanHistory[] = [
      { id: 1, date: "2024-12-01", bodyPart: "Face", image: "example1.jpg", prediction: "Malignant" },
      { id: 2, date: "2024-11-20", bodyPart: "Back", image: "example2.jpg", prediction: "Benign" },
      { id: 3, date: "2024-11-10", bodyPart: "Neck", image: "example3.jpg", prediction: "Malignant" },
      { id: 4, date: "2024-12-01", bodyPart: "Face", image: "example1.jpg", prediction: "Malignant" },
      { id: 5, date: "2024-11-20", bodyPart: "Back", image: "example2.jpg", prediction: "Benign" },
      { id: 6, date: "2024-11-10", bodyPart: "Neck", image: "example3.jpg", prediction: "Malignant" },
      { id: 7, date: "2024-12-01", bodyPart: "Face", image: "example1.jpg", prediction: "Malignant" },
      { id: 8, date: "2024-11-20", bodyPart: "Back", image: "example2.jpg", prediction: "Benign" },
      { id: 9, date: "2024-11-10", bodyPart: "Neck", image: "example3.jpg", prediction: "Malignant" },
    
    ];
  
    function toggleExpandScan(scanId: number): void {
      expandedScanId = expandedScanId === scanId ? null : scanId;
    }
  
    function newScan() {
      goto('/upload');
    }
  </script>
  
  <div class="h-screen flex flex-col">

    <div class="flex-shrink-0">
      <TopBar />
    </div>
    <div class="flex-1 w-full p-10 flex flex-col items-center overflow-y-auto">
      <h1 class="text-secondary text-2xl font-extralight mb-4">Scan History</h1>
  
      {#if scanHistory.length > 0}
        <div class="overflow-x-auto w-full lg:w-10/12">
          <table class="min-w-full">
            <thead class="bg-primary text-white rounded-t-lg">
              <tr>
                <th class="border-b border-gray-200 p-4 text-left font-light">Date</th>
                <th class="border-b border-gray-200 p-4 text-left font-light">Body Part</th>
                <th class="border-b border-gray-200 p-4 text-left font-light">Predicted Lesion Type</th>
                <th class="border-b border-gray-200 p-4 text-center font-light">Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each scanHistory as scan (scan.id)}
                <tr class="even:bg-gray-50 odd:bg-white hover:bg-gray-100 transition-colors">
                  <td class="border-b border-gray-200 p-4 text-tertiary">{scan.date}</td>
                  <td class="border-b border-gray-200 p-4 text-tertiary">{scan.bodyPart}</td>
                  <td class="border-b border-gray-200 p-4 text-tertiary">{scan.prediction}</td>
                  <td class="border-b border-gray-200 p-4 text-center">
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
                    <td colspan="4" class="border-b p-6 bg-gray-100">
                      <div class="flex flex-col lg:flex-row items-center gap-6">
                        <!-- svelte-ignore a11y_img_redundant_alt -->
                        <img
                          src="{scan.image}"
                          alt="Skin image"
                          class="h-40 w-40 object-cover border"
                        />
                        <div class="flex-1">
                          <p class="text-lg text-tertiary font-medium">Scan Details</p>
                          <div class="mt-4 space-y-2">
                            <p class="text-tertiary font-light"><strong>Created at:</strong> {scan.date}</p>
                            <p class="text-tertiary font-light"><strong>Body Part:</strong> {scan.bodyPart}</p>
                            <p class="text-tertiary font-light"><strong>Prediction:</strong> {scan.prediction}</p>
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
  