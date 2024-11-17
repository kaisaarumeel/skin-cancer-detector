<div class="h-screen w-full flex items-center justify-center">
    <div class="flex flex-col items-center justify-center w-6/12">
        <h1 class="text-secondary text-3xl font-extralight mb-20">Upload a photo of your skin</h1>
        <p class="text-tertiary mb-2">For a more precise analysis choose the body part where the mole is located.</p>
     
        <div class="mb-4 w-full">
            <select class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" aria-label="Body Part">
                <option value="" disabled selected class="text-gray-400">Select body part</option>
                <option value="arm">Arm</option>
                <option value="leg">Leg</option>
            </select>
        </div>
     
        <form class="mt-10 w-full" action="/action_page.php">
            <input type="file" id="myFile" name="filename">
            <input type="submit">
        </form>
    </div>
</div>
