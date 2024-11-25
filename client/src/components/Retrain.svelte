<script lang="ts">
  import { API } from "../api";
  import { onMount } from "svelte";
  import type { AxiosResponse, AxiosError } from "axios";
    import { FIELDS } from "../scripts/fields";

  // Interface definitions
  interface TrainingJob {
    job_id: string;
    status: "completed" | "running" | "error";
    start_time: number;
    error?: string;
    parameters: TrainingArgs;
  }

  interface TrainingArgs {
    clear_cache: boolean;
    force_gpu: boolean;
    test: boolean;
    db_images_name: string;
    db_app_name: string;
    images_table_name: string;
    app_table_name: string;
    row_limit: number | null;
    start_row: number;
    test_size: number;
    random_state: number;
    input_width: number;
    input_height: number;
    num_classes: number;
    dropout_rate: number;
    loss_function: string;
    num_epochs: number;
    batch_size: number;
    learning_rate: number;
  }

  interface LoginResponse {
    token?: string;
    is_admin: boolean;
  }

  interface JobsResponse {
    jobs: TrainingJob[];
  }

  // Component state
  let buttonText = "Retrain Model";
  let isLoading = false;
  let jobs: TrainingJob[] = [];
  let pollingInterval: any;
  let selectedJobId: string | null = null; // Changed to store just the ID
  let isDialogOpen = false;


  // Check that the user is a logged in admin
  async function checkAuthentication(): Promise<boolean> {
    try {
      // Check if the user is an admin and logged in
      const adminResponse: AxiosResponse<LoginResponse> = await API.get('/api/is_admin/');
      if (!adminResponse.data.is_admin) {
        console.log("User is not an admin.");
        return false;
      }
      return true;
    } catch (error) {
      console.error("Authentication check failed:", error);
      return false;
    }
  }

  // Reactive statement to ensure that the job details
  // are updated whenever the job updates or selectedJobId changes
  $: selectedJob = jobs.find((job) => job.job_id === selectedJobId);

  async function initialize(): Promise<void> {
    // This will be removed as the admin page is a protected route
    // however at this stage there is no functional login system
    let isAuthenticated = await checkAuthentication();
    if (isAuthenticated) {
      await fetchJobs();
      startPolling();
    } else {
      console.error("Authentication failed.");
    }
  }

  // Run the initialization on component mount
  onMount(() => {
    // Initialize and catch any errors
    initialize().catch((error) => {
      console.error("Initialization failed:", error);
    });
  });

  // This function will poll new jobs from the API every 5 seconds
  function startPolling(): void {
    pollingInterval = setInterval(async () => {
      await fetchJobs();
    }, 5000);
  }

  async function fetchJobs(): Promise<void> {
    try {
      // Fetch jobs from the API
      const response: AxiosResponse<JobsResponse> =
        await API.get("/api/retrain/");
      // Update the jobs array
      jobs = response.data.jobs;
    } catch (error) {
      // If there is an error, log it
      console.error("Error fetching jobs:", error);
    }
  }

  async function deleteCompletedJobs(): Promise<void> {
    try {
      // Delete all completed jobs
      await API.delete("/api/retrain/");
      // Filter out completed jobs
      jobs = jobs.filter((job) => job.status !== "completed");
    } catch (error) {
      // Log any errors
      console.error("Error deleting completed jobs:", error);
    }
  }

  function showJobDetails(job: TrainingJob): void {
    // Update the selected job and open the dialog
    selectedJobId = job.job_id;
    // Set the dialog to open
    isDialogOpen = true;
  }

  async function retrain(): Promise<void> {
    try {
      // Update button text for visual feedback
      buttonText = "Loading...";
      // We dont want any other actions while loading
      isLoading = true;

      // Create an object from fields array
      // This will be used to send the request to the API
      const fieldValues = FIELDS.reduce((acc, field) => {
        // Reduce the fields array to an object which
        // will only contain the id and value of each field
        acc[field.id] = field.value;
        return acc;
      }, {} as Record<string, any>);      
      
      // Create request data by mergin trainArgs with input_size
      // Input_size is restructured as an array which is required by the API
      // The API will then reconstruct this into a tuple
      const requestData = {
        ...fieldValues,
        input_size: [fieldValues.input_width, fieldValues.input_height, 3] as [
          number,
          number,
          number,
        ],
      };

      // Remove input_width and input_height from the request data
      // We do this because the API expects input_size as an array
      // Which we already added as part of the packaging.
      const payload = Object.fromEntries(
        Object.entries(requestData).filter(
          ([key]) => key !== "input_width" && key !== "input_height",
        ),
      );

      // Send the retrain request
      const response: AxiosResponse<{ success: boolean }> = await API.post(
        "/api/retrain/",
        payload,
      );
      // Log the response
      console.log("Retrain successful:", response);
      // Update the button text for visual feedback
      buttonText = "Success!";
    } catch (error) {
      // Log the error to the user and console
      console.error("Error:", error);
      buttonText = error as string;
    } finally {
      // If the promise resolved, we can allow the user to retrain again
      isLoading = false;

      // Reset button text after 3 seconds
      setTimeout(() => {
        // Reset the button text
        buttonText = "Retrain Model";
      }, 3000);
    }
  }
</script>

<div
  class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start justify-between"
>
  <h2 class="text-lg font-regular text-secondary">Retrain Model</h2>

  <div class="w-full mt-4 mb-4 border px-4 pb-4 pt-4">
    <div class="flex justify-between items-center">
      <h3 class="font-semibold">Training Jobs</h3>
      <button
        class="px-4 text-sm py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
        on:click={deleteCompletedJobs}
      >
        Delete Completed Jobs
      </button>
    </div>
    <hr class="my-4" />
    <div class="space-y-2 max-h-40 overflow-y-scroll">
      {#if jobs.length === 0}
        <p class="text-sm text-gray-500">No jobs found.</p>
      {/if}

      {#each jobs as job}
        <button
          class="w-full px-1 text-left"
          on:click={() => showJobDetails(job)}
          ><div
            class="p-3 border rounded-md cursor-pointer hover:bg-gray-200"
            class:bg-green-50={job.status === "completed"}
            class:bg-yellow-50={job.status != "completed"}
            class:bg-red-50={job.status === "error"}
          >
            <div class="flex justify-between items-center">
              <span class="font-medium"
                >Job ID: {job.job_id.slice(0, 8)}... | {job.status.slice(
                  0,
                  10,
                )}...</span
              >
            </div>
            <div class="text-sm text-gray-500">
              Started: {new Date(job.start_time * 1000).toLocaleString()}
            </div>
          </div>
        </button>
      {/each}
    </div>
  </div>

  <!-- bind the dialog to the isDialogOpen -->
  <dialog
    class="mx-4 max-w-xl md:mx-auto absolute top-5 w-full md:max-w-2xl z-20 p-4 rounded-lg shadow-xl"
    open={isDialogOpen}
  >
    {#if selectedJob}
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-semibold">Job Details</h3>
          <button
            class="text-gray-500 hover:text-gray-700"
            on:click={() => {
              isDialogOpen = false;
              selectedJobId = null;
            }}
          >
            X
          </button>
        </div>

        <div class="space-y-2">
          <div class="border p-2">
            <p class="font-medium">Job ID</p>
            <div class="text-wrap courier">{selectedJob.job_id}</div>
          </div>

          <div class="border p-2">
            <p class="font-medium">Status</p>
            <div class="text-wrap courier">{selectedJob.status}</div>
          </div>

          <div class="border p-2">
            <p class="font-medium">Start Time</p>
            <p class="courier">
              {new Date(selectedJob.start_time * 1000).toLocaleString()}
            </p>
          </div>

          {#if selectedJob.error}
            <p class="text-red-600">
              <strong>Error:</strong>
              {selectedJob.error}
            </p>
          {/if}

          <div class="border p-2">
            <p class="font-medium">Hyperparameters</p>
            <pre
              class="bg-gray-50 mt-2 p-4 rounded-md overflow-x-auto">{JSON.stringify(
                selectedJob.parameters,
                null,
                2,
              )}</pre>
          </div>
        </div>

        <div class="flex justify-end mt-4">
          <button
            class="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
            on:click={() => {
              isDialogOpen = false;
              selectedJobId = null;
            }}
          >
            Close
          </button>
        </div>
      </div>
    {/if}
  </dialog>
  <p class="text-sm text-tertiary mt-2">
    Configure training parameters and click retrain to start.
  </p>
  <div
    class="w-full mt-4 max-h-96 overflow-y-auto border border-gray-200 rounded-md p-4"
  >
    {#each FIELDS as { label, id, value, isNumber, isCheckbox, min, max, step }}
      <div class="flex flex-col mb-2">
        {#if isNumber}
          <label for={id}>{label}</label>
          <input
            type="number"
            {id}
            bind:value={value as number}
            {min}
            {max}
            {step}
            class="border rounded-md p-2"
          />
        {:else if isCheckbox}
          <div class="flex items-center">
            <input
              type="checkbox"
              {id}
              bind:checked={value as boolean}
              class="mr-2"
            />
            <label for={id}>{label}</label>
          </div>
        {:else}
          <label for={id}>{label}</label>

          <input type="text" {id} bind:value class="border rounded-md p-2" />
        {/if}
      </div>
    {/each}
  </div>

  <button
    class="mt-4 w-full py-2 px-4 bg-primary text-white rounded-md hover:bg-secondary disabled:opacity-50"
    on:click={retrain}
    disabled={isLoading}
  >
    {buttonText}
  </button>
</div>

<style>
  .courier {
    font-family: "Courier New", Courier, monospace;
  }
</style>
