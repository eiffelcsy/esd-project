<template>
  <div class="flex flex-col">
    <nav class="flex gap-4 p-4">
      <Button variant="link">
        <router-link :to="{ name: 'trip-planning', params: { tripId: $route.params.tripId }}">Planning</router-link>
      </Button>
      <Button variant="link">
        <router-link :to="{ name: 'trip-memories', params: { tripId: $route.params.tripId }}">Memories</router-link>
      </Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Trip Finances</h1>

      <!-- Trip Summary -->
      <Card>
        <CardHeader>
          <CardTitle>Trip Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="font-semibold">Destination:</span>
              <span>{{ trip.destination }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Local Currency:</span>
              <span>{{ trip.localCurrency }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Exchange Rate:</span>
              <span>1 {{ trip.localCurrency }} = {{ trip.exchangeRate }} USD</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Add Expense -->
      <Card>
        <CardHeader>
          <CardTitle>Add Expense</CardTitle>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="addExpense" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="amount">Amount</Label>
                <div class="flex gap-2">
                  <Input
                    id="amount"
                    v-model="newExpense.amount"
                    type="number"
                    step="0.01"
                    required
                  />
                  <Select v-model="newExpense.currency">
                    <SelectTrigger>
                      <SelectValue :placeholder="trip.localCurrency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem :value="trip.localCurrency">{{ trip.localCurrency }}</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div class="space-y-2">
                <Label for="description">Description</Label>
                <Input
                  id="description"
                  v-model="newExpense.description"
                  required
                />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="category">Category</Label>
              <Select v-model="newExpense.category">
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="food">Food & Drinks</SelectItem>
                  <SelectItem value="transportation">Transportation</SelectItem>
                  <SelectItem value="accommodation">Accommodation</SelectItem>
                  <SelectItem value="activities">Activities</SelectItem>
                  <SelectItem value="shopping">Shopping</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="flex justify-end">
              <Button type="submit">Add Expense</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- Expenses List -->
      <Card>
        <CardHeader>
          <CardTitle>Expenses</CardTitle>
          <CardDescription>All expenses for this trip</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="expenses.length" class="space-y-4">
            <div v-for="expense in expenses" :key="expense.id" class="border rounded-lg p-4">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold">{{ expense.description }}</h3>
                  <p class="text-sm text-gray-600">{{ expense.category }}</p>
                </div>
                <div class="text-right">
                  <p class="font-medium">{{ expense.amount }} {{ expense.currency }}</p>
                  <p class="text-sm text-gray-500">
                    {{ expense.amountUSD }} USD
                  </p>
                </div>
              </div>
              <div class="mt-2 text-sm text-gray-500">
                Added by {{ expense.addedBy }} on {{ formatDate(expense.date) }}
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            No expenses added yet.
          </div>
        </CardContent>
      </Card>

      <!-- Settlement Status -->
      <Card>
        <CardHeader>
          <CardTitle>Settlement Status</CardTitle>
          <CardDescription>Track who has finished adding expenses</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="member in groupMembers" :key="member.id" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full" :class="member.ready ? 'bg-green-500' : 'bg-yellow-500'"></div>
                <span>{{ member.name }}</span>
              </div>
              <Button
                v-if="!member.ready && member.id === currentUserId"
                size="sm"
                @click="markAsReady"
              >
                Mark as Ready
              </Button>
            </div>

            <div v-if="allMembersReady" class="mt-4 p-4 bg-green-50 rounded-lg">
              <h3 class="font-semibold text-green-800">All members are ready!</h3>
              <p class="text-sm text-green-700 mt-1">
                Final calculations have been performed. Check your email for settlement details.
              </p>
              <div class="mt-4">
                <Button @click="viewSettlementDetails" variant="outline">
                  View Settlement Details
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Settlement Details Modal -->
    <Dialog v-model:open="showSettlementModal">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settlement Details</DialogTitle>
          <DialogDescription>
            Here's how much each person needs to pay
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div v-for="settlement in settlementDetails" :key="settlement.from" class="border rounded-lg p-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-medium">{{ settlement.from }}</p>
                <p class="text-sm text-gray-600">pays to {{ settlement.to }}</p>
              </div>
              <p class="font-semibold">{{ settlement.amount }} USD</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default {
  name: "Finances",
  components: {
    Button,
    Input,
    Label,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  },
  setup() {
    const route = useRoute();
    const trip = ref({});
    const expenses = ref([]);
    const groupMembers = ref([]);
    const currentUserId = ref(null);
    const showSettlementModal = ref(false);
    const settlementDetails = ref([]);

    const newExpense = ref({
      amount: "",
      currency: "",
      description: "",
      category: "",
    });

    const allMembersReady = computed(() => {
      return groupMembers.value.every(member => member.ready);
    });

    const fetchTripDetails = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}`);
        trip.value = response.data;
        await fetchExpenses();
        await fetchGroupMembers();
      } catch (error) {
        console.error("Error fetching trip details:", error);
      }
    };

    const fetchExpenses = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}/expenses`);
        expenses.value = response.data;
      } catch (error) {
        console.error("Error fetching expenses:", error);
      }
    };

    const fetchGroupMembers = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}/members`);
        groupMembers.value = response.data;
      } catch (error) {
        console.error("Error fetching group members:", error);
      }
    };

    const addExpense = async () => {
      try {
        await axios.post(`/api/trips/${route.params.tripId}/expenses`, newExpense.value);
        newExpense.value = {
          amount: "",
          currency: trip.value.localCurrency,
          description: "",
          category: "",
        };
        await fetchExpenses();
      } catch (error) {
        console.error("Error adding expense:", error);
      }
    };

    const markAsReady = async () => {
      try {
        await axios.post(`/api/trips/${route.params.tripId}/ready`);
        await fetchGroupMembers();
        if (allMembersReady.value) {
          await calculateSettlement();
        }
      } catch (error) {
        console.error("Error marking as ready:", error);
      }
    };

    const calculateSettlement = async () => {
      try {
        const response = await axios.post(`/api/trips/${route.params.tripId}/settlement/calculate`);
        settlementDetails.value = response.data;
      } catch (error) {
        console.error("Error calculating settlement:", error);
      }
    };

    const viewSettlementDetails = () => {
      showSettlementModal.value = true;
    };

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString();
    };

    onMounted(() => {
      fetchTripDetails();
    });

    return {
      trip,
      expenses,
      groupMembers,
      currentUserId,
      newExpense,
      allMembersReady,
      showSettlementModal,
      settlementDetails,
      addExpense,
      markAsReady,
      viewSettlementDetails,
      formatDate,
    };
  },
};
</script> 