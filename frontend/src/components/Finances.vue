<template>
  <div class="flex flex-col">
    <nav class="flex gap-4 p-4">
      <Button variant="link">
        <router-link :to="{ name: 'trip-planning', params: { tripId: route.params.tripId }}">Planning</router-link>
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="payer">Paid by</Label>
                <Select v-model="newExpense.user_id">
                  <SelectTrigger>
                    <SelectValue placeholder="Select payer" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="member in groupMembers" :key="member.id" :value="member.id">
                      {{ member.name }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="payee">Paid for</Label>
                <Select v-model="newExpense.payee_id">
                  <SelectTrigger>
                    <SelectValue placeholder="Select payee (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Everyone (Split equally)</SelectItem>
                    <SelectItem v-for="member in groupMembers" :key="member.id" :value="member.id">
                      {{ member.name }}
                    </SelectItem>
                  </SelectContent>
                </Select>
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
              <div class="mt-2 flex justify-between items-center text-sm text-gray-500">
                <div>
                  Added by User {{ expense.addedBy }} on {{ formatDate(expense.date) }}
                </div>
                <div v-if="expense.payee">
                  <span class="font-medium">Paid for:</span> {{ expense.payee }}
                </div>
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
          <div v-if="settlementDetails.length === 0" class="text-center py-4 text-gray-500">
            No settlements needed. Everyone is even!
          </div>
          <div v-for="settlement in settlementDetails" :key="`${settlement.from}-${settlement.to}`" class="border rounded-lg p-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-medium">{{ settlement.from_name }}</p>
                <p class="text-sm text-gray-600">pays to {{ settlement.to_name }}</p>
              </div>
              <p class="font-semibold">{{ settlement.amount }} {{ settlement.currency }}</p>
            </div>
          </div>
        </div>
        <div v-if="userBalances" class="mt-4 border-t pt-4">
          <h3 class="font-semibold mb-2">Balance Summary</h3>
          <div v-for="(balance, userId) in userBalances" :key="userId" class="flex justify-between items-center py-1">
            <span>{{ userNames[userId] || `User ${userId}` }}</span>
            <span :class="balance > 0 ? 'text-green-600' : balance < 0 ? 'text-red-600' : 'text-gray-600'">
              {{ balance > 0 ? '+' : '' }}{{ balance }} {{ settlementCurrency }}
            </span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const route = useRoute();
const trip = ref({});
const expenses = ref([]);
const groupMembers = ref([]);
const currentUserId = ref(null);
const showSettlementModal = ref(false);
const settlementDetails = ref([]);
const userBalances = ref({});
const userNames = ref({});
const settlementCurrency = ref('SGD');

const newExpense = ref({
  amount: "",
  currency: "",
  description: "",
  category: "",
  user_id: "",
  payee_id: "all",
});

const allMembersReady = computed(() => {
  return groupMembers.value.every(member => member.ready);
});

const fetchTripDetails = async () => {
  try {
    const response = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    trip.value = await response.json();
    await fetchExpenses();
    await fetchGroupMembers();
  } catch (error) {
    console.error("Error fetching trip details:", error);
  }
};

const fetchExpenses = async () => {
  try {
    // Use the expense-management service endpoint to get expenses
    const response = await fetch(`http://localhost:5007/api/expenses/${route.params.tripId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    // Map the expenses to the format expected by the frontend
    expenses.value = data.expenses.map(expense => ({
      id: `${expense.user_id}-${expense.date}`,
      description: expense.description || "No description",
      amount: expense.amount,
      currency: expense.base_currency,
      amountUSD: expense.amount, // This would need proper conversion
      category: expense.category || "Other",
      addedBy: expense.user_id,
      payee: expense.payee_id === 'all' ? 'Everyone' : (
        expense.payee_id ? groupMembers.value.find(m => String(m.id) === String(expense.payee_id))?.name || `User ${expense.payee_id}` : 'Everyone'
      ),
      date: expense.date,
      location: expense.location,
      is_paid: expense.is_paid
    }));
  } catch (error) {
    console.error("Error fetching expenses:", error);
  }
};

const fetchGroupMembers = async () => {
  try {
    // Get readiness status from finance service
    const readinessResponse = await fetch(`http://localhost:5008/api/finance/readiness/${route.params.tripId}`);
    
    if (readinessResponse.ok) {
      const data = await readinessResponse.json();
      groupMembers.value = data.users.map(user => ({
        id: user.user_id,
        name: user.name || `User ${user.user_id}`,
        ready: user.ready
      }));
      
      // Check if trip is ready for settlement
      if (data.all_ready) {
        await calculateSettlement();
      }
    } else {
      console.error("Failed to fetch readiness status:", readinessResponse.statusText);
    }
  } catch (error) {
    console.error("Error fetching group members:", error);
  }
};

const addExpense = async () => {
  try {
    // Check if user_id is set, if not use the current user's ID
    if (!newExpense.value.user_id) {
      newExpense.value.user_id = currentUserId.value;
    }

    // Format the expense data for the expense management service
    const expenseData = {
      trip_id: String(route.params.tripId), // Convert to string to match DB column type
      user_id: String(newExpense.value.user_id), // Use selected payer or current user
      date: new Date().toISOString().split("T")[0], // Current date in YYYY-MM-DD format
      location: trip.value.city || "Unknown",
      amount: parseFloat(newExpense.value.amount),
      base_currency: newExpense.value.currency || "SGD",
      description: newExpense.value.description,
      is_paid: false,
      category: newExpense.value.category,
      payee_id: newExpense.value.payee_id === "all" ? null : String(newExpense.value.payee_id)
    };

    console.log('Sending expense data:', expenseData);
    // Use the expense-management service instead of finance service directly
    const response = await fetch('http://localhost:5007/api/expenses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(expenseData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`HTTP error! Status: ${response.status} Error: ${errorData.error}`);
    }
    
    newExpense.value = {
      amount: "",
      currency: trip.value.localCurrency,
      description: "",
      category: "",
      user_id: currentUserId.value,
      payee_id: "all",
    };
    await fetchExpenses();
  } catch (error) {
    console.error("Error adding expense:", error);
  }
};

const markAsReady = async () => {
  try {
    // Get user details from stored user object
    let userName = `User ${currentUserId.value}`;
    let userEmail = `${currentUserId.value}@example.com`;
    
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const userObj = JSON.parse(storedUser);
        userName = userObj.first_name && userObj.last_name ? 
          `${userObj.first_name} ${userObj.last_name}`.trim() : 
          userObj.name || userName;
        userEmail = userObj.email || userEmail;
      } catch (e) {
        console.error("Error parsing user from localStorage", e);
      }
    }
    
    // Fallback to direct localStorage items if available
    userName = localStorage.getItem('userName') || userName;
    userEmail = localStorage.getItem('userEmail') || userEmail;
    
    // Ensure user ID is sent as a string to match DB column type
    const userId = String(currentUserId.value);
    
    const response = await fetch(`http://localhost:5008/api/finance/readiness/${route.params.tripId}/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: userName,
        email: userEmail
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update the current user's ready status locally
    const updatedMembers = groupMembers.value.map(member => {
      // Compare as strings to ensure type consistency
      if (String(member.id) === String(userId)) {
        return { ...member, ready: true };
      }
      return member;
    });
    groupMembers.value = updatedMembers;
    
    // If all members are ready, the backend should have triggered settlement calculation
    if (data.all_ready) {
      await calculateSettlement();
      showSettlementModal.value = true;
    }
  } catch (error) {
    console.error("Error marking as ready:", error);
  }
};

const calculateSettlement = async () => {
  try {
    const response = await fetch(`http://localhost:5008/api/finance/calculate/${route.params.tripId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Store the settlements data
    settlementDetails.value = data.settlements || [];
    
    // Store user balances and names for display
    userBalances.value = data.user_balances || {};
    userNames.value = data.user_names || {};
    settlementCurrency.value = data.currency || 'SGD';
    
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
  // Get user ID from stored user object
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const userObj = JSON.parse(storedUser);
      // Store ID as string to match database column type
      currentUserId.value = userObj.id ? String(userObj.id) : null;
    } catch (e) {
      console.error("Error parsing user from localStorage", e);
      // Fallback to direct userId if available
      const userId = localStorage.getItem('userId');
      currentUserId.value = userId ? String(userId) : null;
    }
  } else {
    // Fallback to direct userId if available
    const userId = localStorage.getItem('userId');
    currentUserId.value = userId ? String(userId) : null;
  }
  
  if (!currentUserId.value) {
    // Default user ID for development - should be removed in production
    currentUserId.value = "1";
    console.warn("Using default user ID: 1");
  }
  
  // Initialize newExpense with the current user ID
  newExpense.value.user_id = currentUserId.value;
  
  fetchTripDetails();
  fetchGroupMembers();
});
</script> 