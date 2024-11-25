<script  lang="ts">
    let users = [
    { id: 1, name: "User 1" },
    { id: 2, name: "User 2" },
    { id: 3, name: "User 3" },
    { id: 4, name: "User 4" },
    { id: 5, name: "User 5" },
    { id: 6, name: "User 6" },
    { id: 7, name: "User 7" },
    { id: 8, name: "User 8" },
    { id: 9, name: "User 9" },
    { id: 10, name: "User 10" },
    { id: 11, name: "User 9" },
    { id: 12, name: "User 10" },
  ];

  const deleteUser = (id: number) => {
    // Remove the user with the given id from the list
    users = users.filter(user => user.id !== id);
  };
</script>

<div class="bg-white rounded-lg shadow-md p-4 flex flex-col items-start">
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
