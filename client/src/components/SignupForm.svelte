<script lang="ts">
  import { goto } from '$app/navigation';
  import { API } from '../api'; // Import the API instance
  import type { AxiosError } from 'axios'; // Import AxiosError type
  import { generateCSRFToken, getCSRFToken } from '../stores/csrfStore'; // Import CSRF token

  let username = '';
  let password = '';
  let age = '';
  let sex = '';
  let errorMessage = '';

  // Define the type for the error response
  type ErrorResponse = {
    err?: string;
  };

  async function Signup() {
    errorMessage = ''; // Reset error message
    try {
      // generate csrf token and store in browser cookie
      await generateCSRFToken();

      const signupResponse = await API.post('/api/register/', {
        username: username,
        password: password,
        age: age,
        sex: sex,
      }, {
        headers: {
          'X-CSRFToken': getCSRFToken(),
        }
      });

      // After signup, automatically log the user in
      const signinResponse = await API.post('/api/login/', {
        username: username,
        password: password,
      }, {
        headers: {
          'X-CSRFToken': getCSRFToken(),
        }
      });

      // Check if the user is an admin
      const adminResponse = await API.get('api/is_admin/');
      if (adminResponse.data.is_admin) {
        goto('/admin'); // If the user is an admin, redirect to the admin page
      } else {
        goto('/upload'); // Otherwise, redirect to the upload page
      }

    } catch (err) {
      console.error('Error occurred during signup or signin:', err);

      // Cast error to AxiosError
      const axiosError = err as AxiosError<ErrorResponse>;

      // Check if it has a response and extract the error message
      if (axiosError.response) {
        errorMessage = axiosError.response.data?.err || 'Signup failed. Please try again.';
      } else {
        errorMessage = 'An error occurred. Please try again.';
      }
    }
  }

  // Function to handle form submission when pressing Enter
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      Signup();
    }
  }
</script>

<div class="flex flex-col max-w-md w-full text-center justify-center">
  <h2 class="text-3xl font-light text-secondary mb-6 block lg:hidden">Sign up to SkinScan.</h2>
  <h2 class="text-3xl font-light text-secondary mb-6 hidden lg:block"> Sign up </h2>
  <p class="text-tertiary mb-5">Create an account.</p>
  <div class="mb-4">
    <input 
      type="username" 
      placeholder="Username"  
      on:keydown={handleKeydown} 
      bind:value={username} 
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary"
    />
  </div>
  <div class="mb-4">
    <input 
      type="password" 
      bind:value={password}  
      on:keydown={handleKeydown} 
      placeholder="Password" 
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary"
    />
  </div>
  <div class="mb-4">
    <select 
      bind:value={sex} 
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" 
      aria-label="Sex"
    >
      <option value="" disabled selected class="text-gray-400">Select Sex</option>
      <option value="male">Male</option>
      <option value="female">Female</option>
    </select>
  </div>
  <div class="mb-4">
    <input  
      on:keydown={handleKeydown}  
      bind:value={age} 
      type="number" 
      placeholder="Age" 
      class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary" 
      min="0" max="100" step="1"
    />
  </div>

  {#if errorMessage}
    <p class="text-red-500 text-xs font-light">{errorMessage}</p>
  {/if}

  <button 
    on:click={Signup} 
    class="w-full p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-4 transition-colors hover:bg-secondary shadow-l"
  >
    Sign up
  </button>
</div>
