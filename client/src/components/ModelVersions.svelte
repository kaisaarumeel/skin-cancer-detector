<script lang="ts">
    import { onMount } from "svelte";
    import type { AxiosResponse } from "axios";
    import { API } from "../api";
    import { models, activeModel, type Model, type Hyperparameters } from "../stores/modelStore";

    let expandedModelVersion: string | null = null;

    async function getAllModels(): Promise<void> {
        try {
            const response: AxiosResponse<{models: any[]}> = await API.get("api/models/all-models/");
            models.set(
                response.data.models.map((model) => {
                    const rawHyperparameters = JSON.parse(model.hyperparameters);
                    return {
                        ...model,
                        hyperparameters: parseHyperparameters(rawHyperparameters),
                    };
                })
            );
        } catch (error) {
            console.error("Getting all models failed:", error);
        }
    }

    async function getActivemodel(): Promise<void> {
        try {
            const response: AxiosResponse<Model> = await API.get("api/models/active-model/");
            const storedActiveModel = {
                ...response.data,
                hyperparameters: parseHyperparameters(response.data.hyperparameters),
            };
            activeModel.set(storedActiveModel);
        } catch (error) {
            console.error("Getting active model failed:", error);
        }
    }

    async function setActiveModel(model: Model): Promise<void> {
        try {
            const response: AxiosResponse<{ message: string }> = await API.post(`api/models/swap-model/${model.version}/`);
            activeModel.set(model);
        } catch (error) {
            console.error("Setting active model failed:", error);
        }
    }

    function toggleExpandModel(model: Model): void {
        expandedModelVersion = expandedModelVersion === model.version ? null : model.version;
    }

    function parseHyperparameters(rawHyperparameters: any): Hyperparameters {
    return {
        "Test size": rawHyperparameters.test_size,
        "Input size": rawHyperparameters.input_size,
        "Dropout rate": rawHyperparameters.dropout_rate,
        "Loss function": rawHyperparameters.loss_function,
        "Number of epochs": rawHyperparameters.num_epochs,
        "Batch size": rawHyperparameters.batch_size,
        "Learning rate": rawHyperparameters.learning_rate,
        "Validation Accuracy": Math.round(Number(rawHyperparameters.validation_accuracy) * 100),
    };
}

    onMount(() => {
        getAllModels();
        getActivemodel();
    });
</script>

<div class="bg-white w-full rounded-lg shadow-md p-4 flex flex-col items-start">
    <h2 class="text-lg font-regular text-secondary">Model Versions</h2>

    <!-- active model version -->
    <div class="mt-4 w-full">
        <p class="text-sm font-medium text-tertiary">Active Model Version:</p>
        <div class="py-2 px-3 bg-green-100 text-green-800 rounded mt-1 text-md">
            {#if $activeModel}
                v{$activeModel.version}.0
            {:else}
                <em>No active model</em>
            {/if}
        </div>
    </div>

    <p class="mt-6 text-sm font-medium text-tertiary">
        Switch the currently active Model Version:
    </p>

    <!-- model versions list -->
    <ul class="mt-1 w-full space-y-2 text-gray-700 max-h-80 overflow-y-auto pr-2">
        {#if $models.length > 0}
            {#each $models as model (model.version)}
                <li class="relative">
                    <div class="w-full">
                        <button
                            type="button"
                            class="w-full flex items-center justify-between py-2 px-3 rounded focus:outline-none mr-2
                            {expandedModelVersion === model.version ? 'bg-gray-200' : 'bg-gray-100 hover:bg-gray-200'}"
                            on:click={() => toggleExpandModel(model)}
                        >
                            <div>
                                <span class="text-tertiary">v{model.version}.0</span>
                                <span class="text-tertiary text-xs ml-2">
                                    {new Date(model.created_at * 1000).toLocaleDateString()}
                                </span>
                            </div>
                            {#if $activeModel && $activeModel.version === model.version}
                                <span class="text-green-600 text-xs font-regular">(Current)</span>
                            {/if}
                        </button>
                        
                        <!-- collapsible hyperparameter panel -->
                        {#if expandedModelVersion === model.version}
                            <div class="mt-2 p-3 text-sm border rounded bg-gray-50">
                                <p><strong>Hyperparameters:</strong></p>
                                <ul>
                                    {#each Object.entries(model.hyperparameters) as [key, value]}
                                        {#if key === "Validation Accuracy"}
                                            <li>{key}: {value}%</li>
                                        {:else}
                                            <li>{key}: {value}</li>
                                        {/if}
                                    {/each}
                                </ul>
                                <!-- swap model button -->
                                <button
                                    type="button"
                                    class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
                                    on:click={() => setActiveModel(model)}
                                >
                                    Set as Active Model
                                </button>
                            </div>
                        {/if}
                    </div>
                </li>
            {/each}
        {:else}
            <em>No stored models</em>
        {/if}
    </ul>
</div>