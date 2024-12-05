<script lang="ts">
  import { goto } from '$app/navigation';
  import { API } from '../api'; // Import the API instance
  import type { AxiosError } from 'axios'; // Import AxiosError type

  let username = '';
  let password = '';
  let errorMessage = '';

  // Define the type for the error response
  type ErrorResponse = {
    err?: string;
  };

  async function Signin() {
    errorMessage = ''; // Reset error message
    try {
      // Make POST request to the login endpoint
      const response = await API.post('/api/login/', {
        username: username,
        password: password,
      });

      // Handle successful response
      console.log('Login successful:', response.data);

      // Check if the user is an admin and redirect accordingly
      const adminResponse = await API.get('api/is_admin/');
      if (adminResponse.data.is_admin) {
          goto('/admin'); // If the user is an admin, redirect to the admin page
        } else {
          goto('/upload');
        }
    } catch (err) {
      console.error('Error occurred during signup:', err);

      // Cast error to AxiosError
      const axiosError = err as AxiosError<ErrorResponse>;

      // Check if it has a response and extract the error message
      if (axiosError.response) {
        errorMessage = axiosError.response.data?.err || 'Signin failed. Please try again.';
      } else {
        errorMessage = 'An error occurred. Please try again.';
      }
    }
  }

  // Function to handle form submission when pressing Enter
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      Signin();
    }
  }
</script>

<div class="flex flex-col max-w-md w-full text-center justify-center">
  <h2 class="text-3xl font-light text-secondary mb-6 block lg:hidden">Log in to SkinScan.</h2>
  <h2 class="text-3xl font-light text-secondary mb-6 hidden lg:block"> Log in </h2>
  <p class="text-tertiary mb-5">Welcome back, you’ve been missed!</p>
  <div class="mb-4">
    <input
      type="username"
      bind:value={username}
      placeholder="Username"
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary"
      on:keydown={handleKeydown} 
    />
  </div>
  <div class="mb-4">
    <input
      type="password"
      bind:value={password}
      placeholder="Password"
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary"
      on:keydown={handleKeydown} 
    />
  </div>
  {#if errorMessage}
    <p class="text-red-500 text-xs font-light">{errorMessage}</p>
  {/if}
  <button
    on:click={Signin}
    class="w-full p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-4 transition-colors hover:bg-secondary shadow-l"
  >
    Sign in
  </button>
</div>
