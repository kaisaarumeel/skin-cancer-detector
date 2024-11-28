import { writable } from "svelte/store";

export type Hyperparameters = {
    "Test size": number;
    "Input size": number[];
    "Dropout rate": number;
    "Loss function": string;
    "Number of epochs": number;
    "Batch size": number;
    "Learning rate": number;
    "Validation Accuracy": number;
};

export type Model = {
    version: string;
    created_at: number;
    hyperparameters: Hyperparameters;
};

export const models = writable<Model[]>([]);
export const activeModel = writable<Model | null>(null);