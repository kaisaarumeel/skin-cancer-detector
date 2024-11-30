<script lang="ts">
  import { onMount } from "svelte";
  import { API } from '../api';
  import type { AxiosError } from 'axios';

  interface User {
    id: string;
    name: string;
  }
  type ErrorResponse = {
    err?: string;
  };

  let users: User[] = []
  let errorMessage: string | null = null; // To store any error messages

  // Fetch users from the backend API
  const getUsers = async () => {
    try {
      const response = await API.get("/api/get-all-users/");
      console.log("API Response:", response.data);

      const data = response.data;
      users = data.users.map((user: { username: string }) => ({
        id: user.username,
        name: user.username,
      }));
      console.log("Users fetched successfully:", users);
    } catch (err) {
      const axiosError = err as AxiosError<ErrorResponse>;
      // Display error message
      errorMessage = axiosError.response?.data?.err || "An unknown error occurred.";
      console.error("Error getting users:", errorMessage);
    }
  };

  const deleteUser = (username: string) => {
    // Remove the user with the given username from the list
    users = users.filter(user => user.id !== username);
  };

  // Fetch users when the component is mounted
  onMount(() => {
    getUsers();
  });
</script>

<div class="h-fit bg-white rounded-lg shadow-md p-4 flex flex-col items-start">
    <h2 class="text-lg font-regular text-secondary">Manage Users</h2>
    <p class="text-sm text-tertiary mt-2">View and manage user accounts.</p>
    <ul class="mt-4 w-full space-y-2 max-h-96 overflow-y-auto"> 
      {#each users as user (user.id)}
        <li class="flex justify-between items-center bg-gray-100 py-2 px-4 rounded-md">
          <span class="text-tertiary">{user.name}</span>
          <button
            class="text-red-500 hover:text-red-700 focus:outline-none"
            aria-label="Delete user"
            on:click={() => deleteUser(user.id)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M6 2a1 1 0 00-1 1v1H3a1 1 0 100 2h1v9a2 2 0 002 2h8a2 2 0 002-2V6h1a1 1 0 100-2h-2V3a1 1 0 00-1-1H6zm3 3a1 1 0 011-1h2a1 1 0 011 1v1H9V5zm5 4a1 1 0 10-2 0v5a1 1 0 102 0V9zm-6 0a1 1 0 10-2 0v5a1 1 0 102 0V9z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </li>
      {/each}
    </ul>
  </div>
