<script lang="ts">
  import { models, activeModel, type Model } from "../stores/modelStore";

  // each data point represents a model version
  type GraphDataPoint = {
    version: string;
    accuracy: number;
    recall: number;
  }

  let graphData: GraphDataPoint[] = [];

  // reactively update models from store
  $: {
  const storedModels = $models;
  graphData = storedModels.map((model) => ({
    version: `v${model.version}.0`,
    accuracy: model.hyperparameters["Validation accuracy"],
    recall: model.hyperparameters["Custom recall"],
  }));
}
</script>

<div class="h-fit bg-white p-4 rounded-lg shadow-md">
  <h2 class="text-lg font-regular text-secondary">Model Predictive Performance</h2>
  
  <div class="relative h-40 mt-10">
    <div class="absolute left-8 top-0 h-full w-[calc(100%-2rem)] overflow-x-auto">
      <svg class="h-full" viewBox="0 0 300 50" preserveAspectRatio="none">
        <!-- Lines for Accuracy -->
        {#each graphData as { version, accuracy }, index}
          {#if index < graphData.length - 1}
            <line
              x1={((index + 0.5) / graphData.length) * 300}
              y1={(100 - accuracy) / 2}
              x2={((index + 1.5) / graphData.length) * 300}
              y2={(100 - graphData[index + 1].accuracy) / 2}
              stroke="#b7a9d4"
              stroke-width="0.5"
            />
          {/if}
        {/each}

        <!-- Lines for Recall -->
        {#each graphData as { version, recall }, index}
          {#if index < graphData.length - 1}
            <line
              x1={((index + 0.5) / graphData.length) * 300}
              y1={(100 - recall) / 2}
              x2={((index + 1.5) / graphData.length) * 300}
              y2={(100 - graphData[index + 1].recall) / 2}
              stroke="#85ffaf"
              stroke-width="0.5"
            />
          {/if}
        {/each}

        <!-- Points for Accuracy -->
        {#each graphData as { version, accuracy }, index}
          <circle
            cx={((index + 0.5) / graphData.length) * 300}
            cy={(100 - accuracy) / 2}
            r="2"
            fill="#b7a9d4"
          />
        {/each}

        <!-- Points for Recall -->
        {#each graphData as { version, recall }, index}
          <circle
            cx={((index + 0.5) / graphData.length) * 300}
            cy={(100 - recall) / 2}
            r="2"
            fill="#85ffaf"
          />
        {/each}

        <!-- Vertical dotted lines -->
        {#each graphData as { version }, index}
          <line
            x1={((index + 0.5) / graphData.length) * 300}
            y1="0"
            x2={((index + 0.5) / graphData.length) * 300}
            y2="50"
            stroke="#626262"
            stroke-dasharray="1, 1"
            stroke-width="0.2"
          />
        {/each}

        <!-- Labels below each dashed line -->
        {#each graphData as { version }, index}
          <text
            x={((index + 0.5) / graphData.length) * 300}
            y="48"  
            text-anchor="middle" 
            font-size="4"  
            fill="#626262" 
          >
            {version}
          </text>
        {/each}
      </svg>
    </div>

    <div class="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-tertiary">
      {#each [100, 90, 80, 70, 60, 50, 40, 30, 20, 10] as percentage}
        <span>{percentage}%</span>
      {/each}
    </div>
  </div>

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
                    <td class="text-sm text-tertiary font-regular">Training set size:</td>
                    <td class="text-sm text-tertiary font-regular">16GB</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Validation set size:</td>
                    <td class="text-sm text-tertiary font-regular">2GB</td>
                  </tr>
                  <tr>
                    <td class="text-sm text-tertiary font-regular">Test set size:</td>
                    <td class="text-sm text-tertiary font-regular">2GB</td>
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

