<script lang="ts">
    import { goto } from '$app/navigation';
    import UserList from '../../components/UserList.svelte';
    import AdminUpload from '../../components/AdminUpload.svelte';
    function handleLogout() {
      // Add logout endpoint/logic here later
      goto('/home');
    }
  
    // Placeholders for card data to be changed
    let latestUploads = [
      { id: 1, name: "Upload A", date: "2024-11-19" },
      { id: 2, name: "Upload B", date: "2024-11-18" },
      { id: 3, name: "Upload C", date: "2024-11-17" }
    ];
  
    let modelVersions = ["v1.0", "v1.1", "v2.0", "v2.1"];

  </script>
  
  <div class="h-screen flex flex-col">
    <header class="bg-primary shadow h-16 p-4 flex justify-between">
      <h1 class="text-xl font-extralight text-white">Admin Dashboard</h1>
      <button class="pr-20 font-light text-white" on:click={handleLogout}>Log out</button>
    </header>
  
    <div class="p-6 flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <AdminUpload></AdminUpload>
      <UserList></UserList>

      <div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start">
        <h2 class="text-lg font-regular text-secondary">Model Versions</h2>
        <p class="text-sm text-tertiary mt-2">View and manage all available model versions.</p>
        <ul class="mt-4 w-full space-y-2 text-gray-700">
          {#each modelVersions as version}
            <li class="py-1 px-2 bg-gray-100 rounded">{version}</li>
          {/each}
        </ul>
      </div>
  
      <div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start">
        <h2 class="text-lg font-regular text-secondary">Latest Uploads</h2>
        <p class="text-sm text-tertiary mt-2">Recent uploads by the users.</p>
        <ul class="mt-4 w-full space-y-2 text-gray-700">
          {#each latestUploads as upload}
            <li class="py-1 px-2 bg-gray-100 rounded flex justify-between">
              <span>{upload.name}</span>
              <span class="text-sm text-gray-500">{upload.date}</span>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  </div>
  