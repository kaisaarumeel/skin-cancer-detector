// Contributors:
// * Contributor: <alexandersafstrom@proton.me>
interface Field {
    label: string;
    id: string;
    value: string | number | boolean | string[] | null;
    isNumber?: boolean;
    isCheckbox?: boolean;
    isDropdown?: boolean;
    min?: number;
    max?: number;
    step?: number;
    dropdown_options?: string | number | boolean | string[] | null;
}

// Default field values for the model
export let FIELDS: Field[] = [
    {
        label: "Clear Cache",
        id: "clear_cache",
        value: false,
        isCheckbox: true,
    },
    {
        label: "Force GPU",
        id: "force_gpu",
        value: false,
        isCheckbox: true,
    },
    { label: "Test Mode", id: "test", value: false, isCheckbox: true },
    {
        label: "Images Database Path",
        id: "db_images_name",
        value: "../db_images.sqlite3",
    },
    {
        label: "App Database Path",
        id: "db_app_name",
        value: "../db_app.sqlite3",
    },
    {
        label: "Images Table Name",
        id: "images_table_name",
        value: "images",
    },
    {
        label: "App Table Name",
        id: "app_table_name",
        value: "models",
    },
    {
        label: "Row Limit",
        id: "row_limit",
        value: null,
        isNumber: true,
        min: 0,
        max: 1000000,
        step: 1,
    },
    {
        label: "Start Row",
        id: "start_row",
        value: 0,
        isNumber: true,
        min: 0,
        max: 1000000,
        step: 1,
    },
    {
        label: "Test Size",
        id: "test_size",
        value: 0.2,
        isNumber: true,
        min: 0,
        max: 1,
        step: 0.1,
    },
    {
        label: "Random State",
        id: "random_state",
        value: 666,
        isNumber: true,
        min: 0,
        max: 1000000,
        step: 1,
    },
    {
        label: "Input Width",
        id: "input_width",
        value: 224,
        isNumber: true,
        min: 0,
        max: 224,
        step: 1,
    },
    {
        label: "Input Height",
        id: "input_height",
        value: 224,
        isNumber: true,
        min: 0,
        max: 224,
        step: 1,
    },
    {
        label: "Number of Classes",
        id: "num_classes",
        value: 7,
        isNumber: true,
        min: 0,
        max: 100,
        step: 1,
    },
    {
        label: "Dropout Rate",
        id: "dropout_rate",
        value: 0.0,
        isNumber: true,
        min: 0,
        max: 1,
        step: 0.1,
    },
    {
        label: "Loss Function",
        id: "loss_function",
        value: "categorical_crossentropy",
        isDropdown: true,
        dropdown_options: ["categorical_crossentropy", "mean_squared_error","binary_crossentropy"],
    },
    {
        label: "Number of Epochs",
        id: "num_epochs",
        value: 7,
        isNumber: true,
        min: 0,
        max: 100,
        step: 1,
    },
    {
        label: "Batch Size",
        id: "batch_size",
        value: 16,
        isNumber: true,
        min: 0,
        max: 256,
        step: 1,
    },
    {
        label: "Learning Rate",
        id: "learning_rate",
        value: 0.00001,
        isNumber: true,
        min: 0,
        step: 0.00001,
        max: 1,
    },
    {
        label:"Malignant Class Multiplier",
        id:"malignant_multiplier",
        value:20.0,
        isNumber:true,
        min:0,
        max:100,
        step:1
    }
];
