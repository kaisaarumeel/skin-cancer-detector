<script lang="ts">
    import { onMount } from "svelte";
    import { API } from "../api";
    import colorscale_jet from "../media/colorscale_jet.jpg"

    // Create interfaces for the impact data
    interface FeatureImpact {
        feature: string;
        impact: number;
    }

    interface Impact {
        pixel_impact_visualized: string;
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
            // Conver the feature impact dict into an array of objects
            impact.feature_impact = Object.entries(
                JSON.parse(response.data.request.feature_impact) as Record<
                    string,
                    number
                >,
            ).map(([feature, impact]) => ({
                feature,
                impact,
            }));
            impact.pixel_impact_visualized = `data:image/png;base64,${impact.pixel_impact_visualized}`;
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
    class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 rounded-lg shadow-xl bg-white p-6 w-11/12 max-w-4xl {showFeatureImpact
        ? 'block'
        : 'hidden'}"
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
                            src={impact.pixel_impact_visualized}
                            alt="AI explanation visualization"
                            class="w-full h-auto"
                        />
                    </div>
                    <img alt="Color scale" src={colorscale_jet} class="rounded-md w-full h-auto" />

                    <p class="text-sm text-tertiary">
                        Highlighted areas show regions that influenced the
                        decision of the the AI model with red being the strongest impact. 
                    </p>
                </div>

                <div class="">
                    <h3 class="text-lg font-semibold text-tertiary">
                        Feature Contributions
                    </h3>
                    <p class="text-sm text-tertiary">
                        The relative impact that certain
                        features would have on the result if they were modified.
                    </p>
                    <div class="space-y-3 mt-4">
                        {#each (impact as Impact).feature_impact as feature}
                            <div
                                class="flex items-center space-x-4 p-3 rounded-lg bg-primary"
                            >
                                <div class="flex-1">
                                    <span class="font-medium text-white"
                                        >{feature.feature}</span
                                    >
                                </div>
                                <div class="text-right">
                                    <span
                                        class="font-mono text-white font-bold"
                                    >
                                        {feature.impact.toFixed(3)}%
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
        class="px-2 py-1 bg-primary text-white rounded-lg hover:opacity-75 transition-opacity"
        on:click={() => (showFeatureImpact = !showFeatureImpact)}
    >
        Show Explanation
    </button>
</div>
