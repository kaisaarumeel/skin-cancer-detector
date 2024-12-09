<script lang="ts">
    import { onMount } from "svelte";
    import { API } from "../api";

    // Create interfaces for the impact data
    interface FeatureImpact {
        feature: string;
        impact: number;
    }

    interface Impact {
        pixel_impact: string;
        feature_impact: FeatureImpact[];
    }

    // Initialize state variable.
    export let scan: number = 0;
    let showFeatureImpact = false;
    let errorOccurred = false;
    let impact: Impact | undefined = undefined;

    // Retrieve feature impact data from the API
    async function fetchFeatureImpact() {
        try {
            const response = await API.get("/api/get-specific-request/" + scan);
            impact = response.data.request;
            if (impact === undefined) {
                throw new Error("No impact data found");
            }
            impact.pixel_impact = `data:image/png;base64,${impact.pixel_impact}`;
        } catch (err: unknown) {
            console.error(err);
            errorOccurred = true;
        }
    }

    onMount(() => {
        // Onmount, fetch the feature impact data
        fetchFeatureImpact().catch((err) => {
            errorOccurred = true;
            console.error("Error fetching feature impact:", err);
        });
    });
</script>

<!-- modal overlay -->
<div
    class="fixed inset-0 bg-black bg-opacity-50 z-40 {showFeatureImpact
        ? 'block'
        : 'hidden'}"
></div>

<dialog
    class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 rounded-lg shadow-xl bg-white p-4 w-11/12 max-w-4xl max-h-[90vh] overflow-auto {showFeatureImpact ? 'block' : 'hidden'}"
    open={showFeatureImpact}
>
    {#if errorOccurred}
        <div class="flex justify-end items-center">
            <button
                class="text-gray-500 hover:text-gray-700"
                on:click={() => (showFeatureImpact = false)}
            >
                X
            </button>
        </div>
        <div class="text-red-600 p-4 rounded-lg bg-red-50">
            Error loading explanation. Please try again later.
        </div>
    {:else if impact}
        <div class="space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-2xl text-tertiary">Diagnosis Explanation</h2>
                <button
                    class="text-gray-500 hover:text-gray-700"
                    on:click={() => (showFeatureImpact = false)}
                >
                    X
                </button>
            </div>

            <div class="grid md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-tertiary">
                        Visual Explanation
                    </h3>
                    <div class="border rounded-lg overflow-hidden">
                        <img
                            src={impact.pixel_impact}
                            alt="AI explanation visualization"
                            class="w-full h-auto"
                        />
                    </div>
                    <p class="text-sm text-tertiary">
                        Highlighted areas show regions that influenced the
                        decision of the AI model.
                    </p>
                </div>

                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-tertiary">
                        Feature Contributions
                    </h3>
                    <div class="space-y-3">
                        {#each (impact as Impact).feature_impact as feature}
                        <div class="flex items-center space-x-4 p-3 rounded-lg bg-primary">
                            <div class="flex-1">
                                <span class="font-light text-white">
                                    {feature.feature.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')}
                                </span>
                            </div>
                            <div class="text-right">
                                <span class="font-light text-white font-bold">
                                    {Number(feature.impact.toFixed(2)) * 100}%
                                </span>
                            </div>
                        </div>
                    {/each}
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="flex justify-center items-center p-8">
            <div
                class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"
            ></div>
        </div>
    {/if}
</dialog>


<div>
    <button
        class="bg-primary text-white px-6 py-3 font-light rounded-md cursor-pointer transition-colors hover:bg-secondary shadow-md"
        on:click={() => (showFeatureImpact = !showFeatureImpact)}
    >
        Show Explanation
    </button>
</div>
