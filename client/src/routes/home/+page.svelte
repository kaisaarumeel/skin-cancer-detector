<div class="w-full h-screen flex justify-center items-center">
  <!-- Left Section (hidden on small screens, visible on large screens) -->
  <div class="hidden lg:flex h-1/2 w-6/12 flex-col justify-between mr-20">
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


  <div class="flex flex-col max-w-md w-full h-full text-center justify-center">
    <h2 class="text-3xl font-light text-secondary mb-6">Login here</h2>
    <p class="text-tertiary mb-5">Welcome back, you’ve been missed!</p>
    <div class="mb-4">
      <input type="email" placeholder="Email" class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary">
    </div>
    <div class="mb-4">
      <input type="password" placeholder="Password" class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary">
    </div>
    <button class="w-full p-3 bg-primary text-white font-light rounded-md cursor-pointer mt-4 transition-colors hover:bg-secondary shadow-l">Sign in</button>
    <button class="w-full p-2 bg-white rounded-md cursor-pointer mt-4 text-tertiary text-sm font-regular border-none hover:bg-stone-200 shadow-md">Create new account</button>
  </div>
</div>
