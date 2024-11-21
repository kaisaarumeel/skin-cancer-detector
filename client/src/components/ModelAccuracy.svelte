<script>
    let modelVersions = [
      { version: "V1", accuracy: 70 },
      { version: "V2", accuracy: 80 },
      { version: "V3", accuracy: 78 },
      { version: "V4", accuracy: 76 },
      { version: "V5", accuracy: 80 },
      { version: "V6", accuracy: 35 },
    ];
  </script>
  
  <div class="bg-white w-full max-w-md mx-auto p-4 rounded-lg shadow-md">
    <h2 class="text-lg font-regular text-secondary">Model Accuracy</h2>
    <div class="relative h-40 mt-10 mb-10">
        <!-- SVG Chart -->
        <div class="absolute left-8 top-0 h-full w-[calc(100%-2rem)]">
          <svg class="w-full h-full" viewBox="0 0 100 50" preserveAspectRatio="none">
            <!-- Lines connecting points -->
            {#each modelVersions as { version, accuracy }, index}
              {#if index < modelVersions.length - 1}
                <line
                  x1={(index / (modelVersions.length - 1)) * 100}
                  y1={(100 - accuracy) / 2}
                  x2={((index + 1) / (modelVersions.length - 1)) * 100}
                  y2={(100 - modelVersions[index + 1].accuracy) / 2}
                  stroke="#626262"
                  stroke-width="0.5"
                />
              {/if}
            {/each}
            <!-- Points -->
            {#each modelVersions as { version, accuracy }, index}
              <circle
                cx={(index / (modelVersions.length - 1)) * 100}
                cy={(100 - accuracy) / 2}
                r="1.5"
                fill="#626262"
              />
            {/each}
            <!-- Vertical dotted lines -->
            {#each modelVersions as { version }, index}
              <line
                x1={(index / (modelVersions.length - 1)) * 100}
                y1="0"
                x2={(index / (modelVersions.length - 1)) * 100}
                y2="50"
                stroke="#626262"
                stroke-dasharray="1, 1"
                stroke-width="0.2"
              />
            {/each}
          </svg>
        </div>
      
        <div class="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-tertiary">
          {#each [100, 90, 80, 70, 60, 50, 40, 30, 20, 10] as percentage}
            <span>{percentage}%</span>
          {/each}
        </div>
      
        <div class="absolute bottom-0 left-8 w-[calc(100%-2rem)] flex justify-between text-xs text-tertiary">
          {#each modelVersions as { version }}
            <span>{version}</span>
          {/each}
        </div>
      </div>
      
    <div class="bg-gray-100 p-4 rounded-md">
      <p class="text-sm text-tertiary font-regular">Training set size: 16Gb</p>
      <p class="text-sm text-tertiary font-regular">Validation set size: 2Gb</p>
      <p class="text-sm text-tertiary font-regular">Test set size: 2Gb</p>
      <p class="text-sm text-tertiary font-regular">Accuracy rate: 85%</p>
      <p class="text-sm text-tertiary font-regular">Model version: V1.0.1</p>
    </div>

  </div>
  