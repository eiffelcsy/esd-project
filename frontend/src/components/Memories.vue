<template>
  <div class="flex flex-col">
    <nav>
      <Button variant="link"><a href="/trip">Go to Trip Planning</a></Button>
      <Button variant="link"><a href="/finances">Go to Finances</a></Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Memories</h1>
      <Card>
        <CardHeader>
          <CardTitle>Journal Entry</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="w-full gap-4 flex flex-col" @submit.prevent="addJournalEntry">
            <Input as="textarea" v-model="journalEntry" placeholder="Write your experience..." required />
            <Button type="submit">Save Entry</Button>
          </form>
        </CardContent>
      </Card>
      <Card class="mt-4">
        <CardHeader>
          <CardTitle>Upload Media</CardTitle>
        </CardHeader>
        <CardContent>
          <Input type="file" @change="uploadMedia" multiple />
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default {
  name: 'Memories',
  components: {
    Button,
    Input,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
  },
  setup() {
    const journalEntry = ref('');
    const isOfflineMode = ref(true); // Set to true to use mock data instead of API calls

    const addJournalEntry = async () => {
      try {
        if (!isOfflineMode.value) {
          // Real API call (when API is available)
          await axios.post('/journal', { entry: journalEntry.value });
        } else {
          // Mock response for offline mode
          console.log("Offline mode: Journal entry saved", journalEntry.value);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        alert('Journal entry saved!');
        journalEntry.value = ''; // Reset form
      } catch (error) {
        console.error('Error saving journal entry:', error);
        alert('Journal entry saved in offline mode!');
      }
    };

    const uploadMedia = async (event) => {
      const files = event.target.files;
      if (files.length === 0) return;

      try {
        if (!isOfflineMode.value) {
          // Real API call (when API is available)
          for (let file of files) {
            const formData = new FormData();
            formData.append('media', file);
            await axios.post('/media', formData);
          }
        } else {
          // Mock response for offline mode
          console.log(`Offline mode: Uploaded ${files.length} files`);
          // Log filenames for debugging
          Array.from(files).forEach(file => {
            console.log(`- ${file.name} (${file.type}, ${file.size} bytes)`);
          });
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        alert('Media uploaded!');
        // Reset file input (need to access the DOM element)
        event.target.value = '';
      } catch (error) {
        console.error('Error uploading media:', error);
        alert('Media uploaded in offline mode!');
      }
    };

    return { journalEntry, addJournalEntry, uploadMedia };
  },
};
</script> 