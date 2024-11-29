<script>
  import LoginForm from "../../components/LoginForm.svelte";
  import SignupForm from "../../components/SignupForm.svelte";
  import { loggedInRedirect } from '../../routeGuard'; 
  import { onMount } from "svelte";

    // Check if the user is logged in
    onMount(() => {
    // Redirect logged-in users away from this page
    loggedInRedirect(); // `redirectIfLoggedIn` is set to true
  });

  // Reactive state to manage whether to show the login or signup form
  let showSignup = false;
</script>

<div class="w-full h-screen flex justify-center items-center">
  <!-- Left Section (hidden on small screens, visible on large screens) -->
  <div class="hidden lg:flex h-1/2 w-6/12 flex-col justify-between mr-20 ml-10">
    <h1 class="text-secondary font-extralight text-6xl">Welcome to <br> SkinScan.</h1>
    
    <div class="flex w-full justify-between">
      <div class="flex flex-col items-center">
        <img class="h-10" src="scan.png" alt="Scan">
        <span class="text-tertiary">Scan a mole on your skin</span>
      </div>
      <div class="flex flex-col items-center">
        <img src="upload.png" class="h-10" alt="Upload">
        <span class="text-tertiary">Upload the photo</span>
      </div>
      <div class="flex flex-col items-center">
        <img src="diagnosis.png" class="h-10" alt="Diagnosis">
        <span class="text-tertiary">Get diagnosis</span>
      </div>
    </div>
  </div>

  <!-- Right Section: Conditionally display SignupForm or LoginForm -->
  <div class="max-w-md w-full h-full flex flex-col justify-center md:mr-10">
    {#if showSignup}
      <SignupForm />
    {:else}
      <LoginForm />
    {/if}
    {#if showSignup}
      <button on:click={() => showSignup = false} class="w-full p-2 bg-white rounded-md cursor-pointer text-tertiary text-sm font-regular border-none hover:bg-stone-200 shadow-md mt-8">Already have an account</button>
    {:else}
      <button on:click={() => showSignup = true} class="w-full p-2 bg-white rounded-md cursor-pointer text-tertiary text-sm font-regular border-none hover:bg-stone-200 shadow-md mt-8">Create new account</button>
    {/if}
  </div>
</div>
