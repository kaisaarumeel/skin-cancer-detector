<script>
  import { goto } from '$app/navigation';

  function Signup() {
  // Add signup endpoint/logic here
    goto('/upload');
  }
</script>

<div class="flex flex-col max-w-md w-full text-center justify-center">
  <h2 class="text-3xl font-light text-secondary mb-6 block lg:hidden">Sign up to SkinScan.</h2>
  <h2 class="text-3xl font-light text-secondary mb-6 hidden lg:block"> Sign up </h2>
    <p class="text-tertiary mb-5">Create an account.</p>
    <div class="mb-4">
      <input type="email" placeholder="Email" class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary">
    </div>
    <div class="mb-4">
      <input type="password" placeholder="Password" class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary">
    </div>
    <div class="mb-4">
        <select class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" aria-label="Sex">
          <option value="" disabled selected class="text-gray-400">Select Sex</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
    </div>
    <div class="mb-4">
        <input type="number" placeholder="Age" class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary" min="0" max="100" step="1">
      </div>
      
    <button on:click={Signup} class="w-full p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-4 transition-colors hover:bg-secondary shadow-l">Sign up</button>
</div>