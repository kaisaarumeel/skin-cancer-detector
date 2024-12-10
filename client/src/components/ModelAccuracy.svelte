<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { models, activeModel, type Model } from "../stores/modelStore";
  import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip } from "chart.js";
  import { API } from "../api";
  import { type AxiosResponse } from "axios";

  // register required chart components
  Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip);

  let totalDataSize: number;
  let trainingDataSize: number;
  let testingDataSize: number;
  let chart: Chart | null = null;
  let dataReady = false;

  // each data point represents a model version
  type GraphDataPoint = {
    version: string;
    accuracy: number;
    recall: number;
  }

  let graphData: GraphDataPoint[] = [];
  let previousGraphData: GraphDataPoint[] = []; // for checking when to refresh graph data

  async function getDataSetSize() {
    try {
      const response: AxiosResponse<{ total_data_points: string }> = await API.get('/api/get-total-datapoints/');
      totalDataSize = +response.data.total_data_points;
      if ($activeModel) {
        testingDataSize = $activeModel.hyperparameters["Test size"] * totalDataSize;
        trainingDataSize = totalDataSize - testingDataSize;
      }
    } catch (error) {
      console.error(error);
    }
  }

  function drawChart() {
    const canvas = document.getElementById("lineChart") as HTMLCanvasElement | null;
    if (!canvas) {
      console.error("Canvas element not found.");
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("Failed to get 2D context.");
      return;
    }

    const labels = graphData.map((point) => point.version);
    const accuracyData = graphData.map((point) => point.accuracy);
    const recallData = graphData.map((point) => point.recall);

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Accuracy",
            data: accuracyData,
            borderColor: "rgba(183, 169, 212)",
            borderWidth: 3,
            pointBackgroundColor: "rgba(183, 169, 212)",
            pointRadius: 3,
            pointHoverRadius: 3,
            tension: 0.4,
          },
          {
            label: "Recall",
            data: recallData,
            borderColor: "rgba(133, 255, 175)",
            borderWidth: 3,
            pointBackgroundColor: "rgba(133, 255, 175)",
            pointRadius: 3,
            pointHoverRadius: 3,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
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
        },
      },
    });
  }

  // reactively update models from store
  $: {
    const storedModels = $models;
    graphData = storedModels.map((model) => ({
      version: `v${model.version}.0`,
      accuracy: model.hyperparameters["Validation accuracy"],
      recall: model.hyperparameters["Custom recall"],
    }));
    dataReady = graphData.length > 0;

    // check that there is new data to update graph with
    if (dataReady && JSON.stringify(graphData) !== JSON.stringify(previousGraphData)) {
      previousGraphData = [...graphData];

      setTimeout(() => {
        if (chart) {
          chart.destroy(); // destroy an existing chart to avoid duplication
        }
        drawChart();
      }, 0);
    }
  }

  // reactive statement to detect changes in the activeModel
  $: if ($activeModel) {
    // recalculate the data size used during training tihi
    getDataSetSize();
  }


  onMount(() => {
    let resizeTimeout: ReturnType<typeof setTimeout>;
    const resizeListener = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (chart) {
          chart.destroy(); // destroy the old chart
        }
        drawChart(); // redraw with updated dimensions
      }, 200); // debounce delay
    };

    window.addEventListener("resize", resizeListener);

    // Cleanup on component destroy
    onDestroy(() => {
      window.removeEventListener("resize", resizeListener);
      if (chart) chart.destroy(); // Ensure the chart is cleaned up
    });
  });

</script>

<div class="h-fit bg-white p-4 rounded-lg shadow-md">
  <h2 class="text-lg font-regular text-secondary">Model Predictive Performance</h2>

  {#if dataReady}
    <div class="relative h-[300px] mt-4">
      <canvas id="lineChart"></canvas>
    </div>
  {:else}
    <p class="text-center text-tertiary mt-8 mb-8">Loading data...</p>
  {/if}

<!-- Legend Below the Graph -->
<div class="flex items-center justify-center space-x-4 mt-4 mb-4">
  <div class="flex items-center">
    <span class="w-4 h-4 inline-block bg-[#b7a9d4] rounded-full"></span>
    <span class="ml-2 text-sm text-secondary">Accuracy</span>
  </div>
  <div class="flex items-center">
    <span class="w-4 h-4 inline-block bg-[#85ffaf] rounded-full"></span>
    <span class="ml-2 text-sm text-secondary">Recall</span>
  </div>
</div>

  <div class="bg-gray-100 p-4 rounded-md">
    {#if $activeModel}
      <table class="w-full">
        <tbody>
          <!-- First Row with Headings -->
          <tr>
            <td class="text-sm text-tertiary font-regular" style="border-right: 1px solid #ccc; padding-right: 1rem;">
              <strong>Active Model</strong>
            </td>
            <td class="text-sm text-tertiary font-regular" style="padding-left: 1rem;">
              <strong>Dataset</strong>
            </td>
          </tr>

          <!-- Second Row with Nested Tables -->
          <tr>
            <!-- Active Model Details -->
            <td class="text-sm text-tertiary font-regular" style="border-right: 1px solid #ccc; padding-right: 1rem;">
              <table class="w-full">
                <tbody>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Model version:</td>
                    <td class="text-sm text-tertiary font-regular">{$activeModel.version}.0</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Accuracy rate:</td>
                    <td class="text-sm text-tertiary font-regular">{$activeModel.hyperparameters["Validation accuracy"]}%</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Custom recall rate:</td>
                    <td class="text-sm text-tertiary font-regular">{$activeModel.hyperparameters["Custom recall"]}%</td>
                  </tr>
                </tbody>
              </table>
            </td>

            <!-- Dataset Details -->
            <td class="text-sm text-tertiary font-regular" style="padding-left: 1rem;">
              <table class="w-full">
                <tbody>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Total dataset size:</td>
                    <td class="text-sm text-tertiary font-regular">{totalDataSize}</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Training dataset size:</td>
                    <td class="text-sm text-tertiary font-regular">{trainingDataSize} ({100 - $activeModel.hyperparameters["Test size"] * 100})%</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Test dataset size:</td>
                    <td class="text-sm text-tertiary font-regular">{testingDataSize} ({$activeModel.hyperparameters["Test size"] * 100 })%</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </tbody>
      </table>
    {:else}
      <p class="text-sm text-tertiary font-regular">No active model</p>
    {/if}
  </div>
</div>

