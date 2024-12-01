<script lang="ts">
    import { onMount } from "svelte";
    import type { AxiosResponse } from "axios";
    import { API } from "../api";
    import { models, activeModel, type Model, type Hyperparameters } from "../stores/modelStore";

    let expandedModelVersion: string | null = null;
    let isConfirmingActivation: boolean = false;
    let isConfirmingDeletion: boolean = false;

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
                hyperparameters: parseHyperparameters(JSON.parse(response.data.hyperparameters)),
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
        resetConfirmationState()
    }

    async function deleteModel(model: Model): Promise<void> {
        try {
            const response: AxiosResponse<{ message: string }> = await API.delete(`api/models/delete-model/${model.version}/`);

            // update the models list
            models.update((currentModels) => currentModels.filter((m) => m.version !== model.version));

            // clear activemodel if it is the one being deleted
            activeModel.update((currentActiveModel) => {
                if (currentActiveModel?.version === model.version) {
                    return null; // reset activemodel
                }
                return currentActiveModel; // keep current activemodel if not deleted
            });
        } catch (error) {
            console.error("Deleting active model failed:", error);
        }
        resetConfirmationState()
    }

    function toggleExpandModel(model: Model): void {
        expandedModelVersion = expandedModelVersion === model.version ? null : model.version;
        resetConfirmationState()
    }

    function toggleConfirmActivation(): void {
        isConfirmingActivation = !isConfirmingActivation;
        isConfirmingDeletion = false;
    }

    function toggleConfirmDeletion(): void {
        isConfirmingDeletion = !isConfirmingDeletion;
        isConfirmingActivation = false;
    }

    function resetConfirmationState(): void {
        isConfirmingDeletion = false;
        isConfirmingActivation = false;
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
                                <span class="text-green-600 text-xs font-regular">ACTIVE</span>
                            {/if}
                        </button>
                        
                        <!-- collapsible hyperparameter panel -->
                        {#if expandedModelVersion === model.version}
                        <div class="mt-2 p-3 text-sm border rounded bg-gray-50">
                            <table class="w-full table-auto border-collapse">
                                <tbody>
                                    <!-- Headings Row -->
                                    <tr>
                                        <td colspan="2" class="pr-2 align-top font-semibold text-left text-sm text-tertiary">
                                            Hyperparameters
                                        </td>
                                        <td class="pl-4 align-top font-semibold text-left text-sm text-tertiary border-l border-gray-300">
                                            Performance
                                        </td>
                                    </tr>
                                    <tr>
                                        <!-- Hyperparameters -->
                                        <td class="pr-2 align-top">
                                            <table class="w-full">
                                                <tbody>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Test size:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Test size"]}</td>
                                                    </tr>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Input size:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Input size"]}</td>
                                                    </tr>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Learning rate:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Learning rate"]}</td>
                                                    </tr>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Loss function:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Loss function"]}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                        <td class="pr-2 align-top">
                                            <table class="w-full">
                                                <tbody>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Batch size:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Batch size"]}</td>
                                                    </tr>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Number of epochs:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Number of epochs"]}</td>
                                                    </tr>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Dropout rate:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Dropout rate"]}</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                        <!-- Performance Metrics -->
                                        <td class="pl-4 align-top border-l border-gray-300">
                                            <table class="w-full">
                                                <tbody>
                                                    <tr>
                                                        <td class="text-sm text-tertiary font-regular">Validation accuracy:</td>
                                                        <td class="text-sm text-tertiary font-regular">{model.hyperparameters["Validation Accuracy"]}%</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <!-- Activate model button -->
                            {#if expandedModelVersion === $activeModel?.version}
                                <button
                                    type="button"
                                    class="mt-4 w-full py-2 px-4 bg-gray-200 text-tertiary rounded-md text-center cursor-not-allowed"
                                    disabled
                                >
                                    Model Active
                                </button>
                            {:else if isConfirmingActivation}
                                <div class="flex space-x-2 mt-4 w-full">
                                    <button
                                        type="button"
                                        class="flex-1 py-2 px-4 bg-green-300 text-white rounded-md text-center cursor-pointer hover:bg-green-400"
                                        on:click={() => setActiveModel(model)}
                                    >
                                        Confirm Activation
                                    </button>
                                    <button
                                        type="button"
                                        class="flex-1 py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
                                        on:click={() => toggleConfirmActivation()}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            {:else}
                                <button
                                    type="button"
                                    class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
                                    on:click={() => toggleConfirmActivation()}
                                >
                                    Set as Active Model
                                </button>
                            {/if}
                            <!-- Delete model button -->
                            {#if isConfirmingDeletion}
                                <div class="flex space-x-2 mt-2 w-full">
                                    <button
                                        type="button"
                                        class="flex-1 py-2 px-4 bg-red-500 text-white rounded-md text-center cursor-pointer hover:bg-red-600"
                                        on:click={() => deleteModel(model)}
                                    >
                                        Confirm Deletion
                                    </button>
                                    <button
                                        type="button"
                                        class="flex-1 py-2 px-4 bg-primary text-white rounded-md text-center cursor-pointer hover:bg-secondary"
                                        on:click={() => toggleConfirmDeletion()}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            {:else}
                                <button
                                    type="button"
                                    class="mt-2 w-full py-2 px-4 bg-red-500 text-white rounded-md text-center cursor-pointer hover:bg-red-600"
                                    on:click={() => toggleConfirmDeletion()}
                                >
                                    Delete Model
                                </button>
                            {/if}
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