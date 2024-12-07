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
  let chartData: { type: string; percentage: number }[] = [];

  interface Request {
    lesion_type: string;
  }

  let requests: Request[] = [];

  function processRequestData(requests: Request[]) {
    // Count the number of each lesion type
    const distributionMap = requests.reduce((acc, request) => {
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
    console.log(total);
    const percentages = Array.from(formattedMap.entries()).map(
      ([type, count]) => ({
        type,
        percentage: (count / total) * 100,
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
            backgroundColor: "rgba(183, 169, 212, 0.8)",
            borderColor: "rgba(183, 169, 212, 1)",
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

  async function fetchAndDisplayData() {
    try {
      // Retrieve all requests
      const response = await API.get("/api/get-all-requests/");
      requests = response.data.requests;
      chartData = processRequestData(requests);
      dataReady = true;
    } catch (err: unknown) {
      console.error("Error fetching request data:", err);
      dataReady = false;
    }
  }

  // When data is ready and the component is mounted, draw the chart
  $: if (dataReady) {
    setTimeout(drawChart, 0);
  }

  onMount(async () => {
    // Retrieve and display data
    await fetchAndDisplayData();
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
