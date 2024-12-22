<script lang="ts">
  import { onMount } from "svelte";
  import {
    Chart,
    BarController,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
  } from "chart.js";
  import { API } from "../api";
  import { userRequests, type UserRequest } from '../stores/requestStore';

  // Register required chart components
  Chart.register(
    BarController,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
  );

  let chart: Chart | null = null;
  let dataReady = false;
  let chartData: { type: string; percentage: number; malignant: boolean }[] = [];

  // Mapping of lesion types to their benign or malignant classification
  const LESION_TYPE_CLASSIFICATION = {
    nv: false, // Melanocytic nevi (benign)
    bkl: false, // Benign keratosis-like lesions (benign)
    df: false, // Dermatofibroma (benign)
    vasc: false, // Vascular lesions (benign)
    mel: true, // Melanoma (malignant)
    bcc: true, // Basal cell carcinoma (malignant)
    akiec: true, // Actinic keratoses and intraepithelial carcinoma (malignant)
  };

  function processRequestData(currentRequests: UserRequest[]) {
    // Count the number of each lesion type
    const distributionMap = currentRequests.reduce((acc, request) => {
      // Either set it to 1 or increment the count
      acc.set(request.lesion_type, (acc.get(request.lesion_type) || 0) + 1);
      return acc;
    }, new Map<string | null, number>());

    // Remove distributions that have no key
    distributionMap.delete("");
    distributionMap.delete(null);

    let formattedMap = new Map<string, number>();
    let total = 0;
    distributionMap.forEach((value, key) => {
      formattedMap.set(key as string, value);
      total += value;
    });

    // Convert the count to percentage distribution
    const percentages = Array.from(formattedMap.entries()).map(
      ([type, count]) => ({
        type,
        percentage: (count / total) * 100,
        malignant: LESION_TYPE_CLASSIFICATION[type as keyof typeof LESION_TYPE_CLASSIFICATION] || false,
      }),
    );

    // Return  percentage
    return percentages;
  }

  function drawChart() {
    if (!dataReady) return;

    // Create new canvas element
    const canvas = document.getElementById("barChart") as HTMLCanvasElement;
    const ctx = canvas.getContext("2d");

    // Create the chart component
    chart = new Chart(ctx as CanvasRenderingContext2D, {
      type: "bar",
      data: {
        labels: chartData.map((item) => item.type),
        datasets: [
          {
            label: "Distribution",
            // just give the percentage data
            data: chartData.map((item) => item.percentage),
            backgroundColor: chartData.map((item) =>
              item.malignant ? "rgba(252, 165, 165, 0.8)" : "rgba(209, 250, 229, 0.8)"
            ),
            borderColor: chartData.map((item) =>
              item.malignant ? "rgba(255, 99, 132, 1)" : "rgba(75, 192, 192, 1)"
            ),
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => `${context.parsed.y.toFixed(1)}%`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: (value) => `${value}%`,
              stepSize: 10,
            },
          },
          x: {
            ticks: {
              autoSkip: false,
              maxRotation: 45,
              minRotation: 45,
            },
          },
        },
      },
    });
  }

  async function fetchAndPopulateStore() {
    try {
      const response = await API.get("/api/get-all-requests/");
      const retrievedRequests = response.data.requests;
      userRequests.set(retrievedRequests); // Populate the store
    } catch (err: unknown) {
      console.error("Error fetching request data:", err);
    }
  }

  // Update the chart data when the store changes
  $: {
    const currentRequests = $userRequests;
    chartData = processRequestData(currentRequests);
    dataReady = chartData.length > 0;
    if (dataReady) {
      setTimeout(drawChart, 0);
    }
  }

  // When data is ready and the component is mounted, draw the chart
  $: if (dataReady) {
    setTimeout(drawChart, 0);
  }

  onMount(async () => {
    await fetchAndPopulateStore();
  });
</script>

<div class="h-fit bg-white p-4 rounded-lg shadow-md">
  <h2 class="text-lg font-regular text-secondary">Lesion Type Distribution</h2>

  {#if dataReady}
    <div class="relative h-[300px] mt-4">
      <canvas id="barChart"></canvas>
    </div>
  {:else}
    <p class="text-center text-tertiary mt-8 mb-8">Loading data...</p>
  {/if}
</div>
