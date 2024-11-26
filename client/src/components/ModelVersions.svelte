<script lang="ts">
    import { onMount } from "svelte";
    import type { AxiosResponse } from "axios";
    import { API } from "../api";

    type Model = {
        version: string;
        created_at: number;
        hyperparameters: string;
    };

    let models: Model[] = [];

    let activeModel: Model | null = null;

    async function getAllModels(): Promise<void> {
        try {
            const response: AxiosResponse<{models: any[]}> = await API.get("api/models/all-models/");
            models = response.data.models;

        } catch (error) {
            console.error("Getting all models failed:", error);
        }
    }

    async function getActivemodel(): Promise<void> {
        try {
            const response: AxiosResponse<Model> = await API.get("api/models/active-model/");
            activeModel = response.data;

        } catch (error) {
            console.error("Getting active model failed:", error);
        }
    }

    async function setActiveModel(model: Model): Promise<void> {
        try {
            const response: AxiosResponse<{ message: string }> = await API.post(`api/models/swap-model/${model.version}/`);
            console.log(response.data.message);
            activeModel = model;
        } catch (error) {
            console.error("Setting active model failed:", error);
        }
        activeModel = model;

    }

    onMount(() => {
        getAllModels();
        getActivemodel();
    });
</script>

<div class="bg-white w-full rounded-lg shadow-md p-4 flex flex-col items-start">
    <h2 class="text-lg font-regular text-secondary">Model Versions</h2>

    <!-- Current Model Version -->
    <div class="mt-4 w-full">
        <p class="text-sm font-medium text-tertiary">Current Model Version:</p>
        <div class="py-2 px-3 bg-green-100 text-green-800 rounded mt-1 text-md">
            {#if activeModel}
                v{activeModel.version}.0
            {:else}
                <em>No active model</em>
            {/if}
        </div>
    </div>

    <p class="mt-6 text-sm font-medium text-tertiary">
        Switch the current Model Version:
    </p>
    <ul class="mt-1 w-full space-y-2 text-gray-700 max-h-80 overflow-y-auto">
        {#each models as model (model.version)}
            <li>
                <button
                    type="button"
                    class="w-full flex items-center justify-between py-2 px-3 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none"
                    on:click={() => setActiveModel(model)}
                    on:keydown={(e) =>
                        e.key === "Enter" && setActiveModel(model)}
                >
                    <div>
                        <span class="text-tertiary">v{model.version}.0</span>
                        <span class="text-tertiary text-xs ml-2"
                            >{new Date(model.created_at * 1000).toLocaleDateString()}</span
                        >
                    </div>
                    {#if activeModel && activeModel.version === model.version }
                        <span class="text-green-600 text-xs font-regular"
                            >(Current)</span
                        >
                    {/if}
                </button>
            </li>
        {/each}
    </ul>
</div>
