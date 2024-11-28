<script lang="ts">
  import { models, activeModel, type Model } from "../stores/modelStore";

  // each data point represents a model version
  type GraphDataPoint = {
    version: string;
    accuracy: number;
  }

  let graphData: GraphDataPoint[] = [];

  // reactively update models from store
  $: {
  const storedModels = $models;
  graphData = storedModels.map((model) => ({
    version: `v${model.version}.0`,
    accuracy: model.hyperparameters["Validation Accuracy"],
  }));
}
</script>

<div class="h-fit bg-white p-4 rounded-lg shadow-md">
  <h2 class="text-lg font-regular text-secondary">Model Accuracy</h2>
  <div class="relative h-40 mt-10 mb-10">
    <div class="absolute left-8 top-0 h-full w-[calc(100%-2rem)] overflow-x-auto">
      <svg class="h-full" viewBox="0 0 300 50" preserveAspectRatio="none">
        <!-- Lines connecting points -->
        {#each graphData as { version, accuracy }, index}
          {#if index < graphData.length - 1}
            <line
              x1={((index + 0.5) / graphData.length) * 300}
              y1={(100 - accuracy) / 2}
              x2={((index + 1.5) / graphData.length) * 300}
              y2={(100 - graphData[index + 1].accuracy) / 2}
              stroke="#626262"
              stroke-width="0.5"
            />
          {/if}
        {/each}

        <!-- Points -->
        {#each graphData as { version, accuracy }, index}
          <circle
            cx={((index + 0.5) / graphData.length) * 300}
            cy={(100 - accuracy) / 2}
            r="2"
            fill="#626262"
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

  <div class="bg-gray-100 p-4 rounded-md">
    {#if $activeModel}
      <p class="text-sm text-tertiary font-regular">Training set size: 16Gb</p>
      <p class="text-sm text-tertiary font-regular">Validation set size: 2Gb</p>
      <p class="text-sm text-tertiary font-regular">Test set size: 2Gb</p>
      <p class="text-sm text-tertiary font-regular">Accuracy rate: {$activeModel.hyperparameters["Validation Accuracy"]}%</p>
      <p class="text-sm text-tertiary font-regular">Model version: {$activeModel.version}.0</p>
    {:else}
      <p class="text-sm text-tertiary font-regular">No active model</p>
    {/if}
  </div>
</div>
