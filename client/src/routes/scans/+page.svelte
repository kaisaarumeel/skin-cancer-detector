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
  
    let scanHistory: ScanHistory[] = [
      { id: 1, date: "2024-12-01", bodyPart: "Face", image: "example1.jpg", prediction: "Malignant" },
      { id: 2, date: "2024-11-20", bodyPart: "Back", image: "example2.jpg", prediction: "Benign" },
      { id: 3, date: "2024-11-10", bodyPart: "Neck", image: "example3.jpg", prediction: "Malignant" },
    ];
  
    function newScan() {
      // Navigate to the upload page
      goto('/upload');
    }
</script>
  
<div class="h-screen flex flex-col relative">
    <TopBar />
    
    <div class="h-full w-full p-10 flex flex-col items-center">
      <h1 class="text-secondary text-2xl font-extralight mb-10">Scan History</h1>
  
      {#if scanHistory.length > 0}
        <div class="overflow-x-auto w-full lg:w-10/12">
          <table class="min-w-full border-collapse border border-gray-200 shadow-md rounded-lg">
            <thead class="bg-primary">
              <tr>
                <th class="border p-4 text-white font-light">Date</th>
                <th class="border p-4 text-white font-light">Body Part</th>
                <th class="border p-4 text-white font-light">Image</th>
                <th class="border p-4 text-white font-light">Predicted Lesion Type</th>
              </tr>
            </thead>
            <tbody>
              {#each scanHistory as { id, date, bodyPart, image, prediction }}
                <tr class="hover:bg-slate-50">
                  <td class="border border-gray-300 p-4 text-tertiary">{date}</td>
                  <td class="border border-gray-300 p-4 text-tertiary">{bodyPart}</td>
                  <td class="border border-gray-300 p-4 text-tertiary">
                    <img src="{image}" alt="Scan image for {bodyPart}" class="h-10 w-10 object-cover rounded-md">
                  </td>
                  <td class="border border-gray-300 p-4 text-tertiary">{prediction}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <p class="text-tertiary mt-10">You have no scans yet. Start by uploading an image of your skin for analysis.</p>
      {/if}
  
      <button
        on:click={newScan}
        class="w-2/3 lg:w-1/3 p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-10 hover:bg-secondary shadow-lg"
      >
        Start a new scan
      </button>
    </div>
</div>

  