<div class="h-screen w-full flex items-center justify-center">
    <div class="flex flex-col items-center justify-center lg:w-6/12 w-10/12">
        <h1 class="text-secondary text-3xl font-extralight mb-20">Upload a photo of your skin</h1>
        <p class="text-tertiary mb-2">For a more precise analysis choose the body part where the mole is located.</p>
     
        <div class="mb-4 w-full">
            <select class="w-full p-2 border border-gray-300 rounded-md outline-none mt-1 focus:border-secondary text-gray-500 focus:text-black" aria-label="Body Part">
                <option value="" disabled selected class="text-gray-400">Select Body Part</option>
                <option value="ear">Ear</option>
                <option value="face">Face</option>
                <option value="neck">Neck</option>
                <option value="scalp">Scalp</option>
            
                <optgroup label="Trunk region">
                    <option value="abdomen">Abdomen</option>
                    <option value="back">Back</option>
                    <option value="chest">Chest</option>
                    <option value="trunk">Trunk - Other</option>
                </optgroup>
            
                <optgroup label="Upper limbs">
                    <option value="acral">Acral (Fingers/Toes)</option>
                    <option value="hand">Hand</option>
                    <option value="upper_extremity">Upper Extremity (Arm)</option>
                </optgroup>
            
                <optgroup label="Lower limbs">
                    <option value="foot">Foot</option>
                    <option value="lower_extremity">Lower Extremity (Leg)</option>
                </optgroup>
            
                <option value="genital">Genital Area</option>
            </select>
            
        </div>
     
        <form class="mt-10 w-full" action="/action_page.php">
            <input type="file" id="myFile" name="filename">
            <input type="submit">
        </form>
    </div>
</div>
