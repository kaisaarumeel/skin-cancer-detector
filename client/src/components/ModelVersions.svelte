<script lang="ts">
    type ModelVersion = {
        name: string;
        dateAdded: string;
    };

    let modelVersions: ModelVersion[] = [
        { name: "v1.0", dateAdded: "2024-01-15" },
        { name: "v1.1", dateAdded: "2024-02-10" },
        { name: "v2.0", dateAdded: "2024-03-05" },
        { name: "v3.0", dateAdded: "2024-05-20" },
        { name: "v1.0", dateAdded: "2024-01-15" },
        { name: "v1.1", dateAdded: "2024-02-10" },
        { name: "v2.0", dateAdded: "2024-03-05" },
        { name: "v3.0", dateAdded: "2024-05-20" },
        { name: "v1.0", dateAdded: "2024-01-15" },
        { name: "v1.1", dateAdded: "2024-02-10" },
        { name: "v2.0", dateAdded: "2024-03-05" },
        { name: "v3.0", dateAdded: "2024-05-20" },
    ];

    let currentModelVersion: ModelVersion = modelVersions[2];

    function setCurrentVersion(version: ModelVersion): void {
        currentModelVersion = version;
    }
</script>

<div class="bg-white w-full rounded-lg shadow-md p-4 flex flex-col items-start">
    <h2 class="text-lg font-regular text-secondary">Model Versions</h2>

    <!-- Current Model Version -->
    <div class="mt-4 w-full">
        <p class="text-sm font-medium text-tertiary">Current Model Version:</p>
        <div class="py-2 px-3 bg-green-100 text-green-800 rounded mt-1 text-md">
            {currentModelVersion.name}
        </div>
    </div>

    <p class="mt-6 text-sm font-medium text-tertiary">
        Switch the current Model Version:
    </p>
    <ul class="mt-1 w-full space-y-2 text-gray-700 max-h-80 overflow-y-auto">
        {#each modelVersions as version (version)}
            <li>
                <button
                    type="button"
                    class="w-full flex items-center justify-between py-2 px-3 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none"
                    on:click={() => setCurrentVersion(version)}
                    on:keydown={(e) =>
                        e.key === "Enter" && setCurrentVersion(version)}
                >
                    <div>
                        <span class="text-tertiary">{version.name}</span>
                        <span class="text-tertiary text-xs ml-2"
                            >{version.dateAdded}</span
                        >
                    </div>
                    {#if version === currentModelVersion}
                        <span class="text-green-600 text-xs font-regular"
                            >(Current)</span
                        >
                    {/if}
                </button>
            </li>
        {/each}
    </ul>
</div>
