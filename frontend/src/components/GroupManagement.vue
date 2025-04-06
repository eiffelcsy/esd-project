<template>
  <div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">Group Management</h1>
      <Button @click="returnToDashboard" variant="secondary" class="flex items-center gap-1">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        Return to Dashboard
      </Button>
    </div>
    
    <!-- Success Notification -->
    <div v-if="showNotification" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4 flex items-center justify-between" role="alert">
      <div>
        <span class="font-bold">Success!</span>
        <span class="block sm:inline"> {{ notificationMessage }}</span>
      </div>
      <button @click="showNotification = false" class="ml-4">
        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    </div>

    <!-- Error Notification -->
    <div v-if="createError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center justify-between" role="alert">
      <div>
        <span class="font-bold">Error!</span>
        <span class="block sm:inline"> {{ createError }}</span>
      </div>
      <button @click="createError = ''" class="ml-4">
        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    </div>
    
    <!-- Invitation Error Notification -->
    <div v-if="invitationError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 flex items-center justify-between" role="alert">
      <div>
        <span class="font-bold">Invitation Error!</span>
        <span class="block sm:inline"> {{ invitationError }}</span>
      </div>
      <button @click="invitationError = ''" class="ml-4">
        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    </div>
    
    <!-- Debug Information (only in development) -->
    <div v-if="debugInfo.show" class="bg-blue-50 border border-blue-300 text-blue-800 p-4 rounded mb-4">
      <div class="flex justify-between">
        <h3 class="font-bold">Debug Information</h3>
        <button @click="debugInfo.show = false" class="text-blue-500 hover:text-blue-700">
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>

      <div class="mt-2 text-xs font-mono whitespace-pre-wrap bg-gray-100 p-2 rounded overflow-auto max-h-60">
        {{ JSON.stringify(debugInfo.data, null, 2) }}
      </div>
    </div>

    <!-- Create New Group -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-xl font-semibold mb-3">Create New Group</h2>
      <form @submit.prevent="createGroup" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Group Name</label>
          <Input
            v-model="newGroup.name"
            type="text"
            class="mt-1"
            required
          />
        </div>
        
        <!-- Date Range Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Date Range</label>
          <Popover>
            <PopoverTrigger as-child>
              <Button
                variant="outline"
                :class="cn(
                  'w-full justify-start text-left font-normal mt-1',
                )"
              >
                <CalendarIcon class="mr-2 h-4 w-4" />
                {{ dateFormatter.format(newGroup.dateRange.start.toDate(getLocalTimeZone())) }} - {{ dateFormatter.format(newGroup.dateRange.end.toDate(getLocalTimeZone())) }}
              </Button>
            </PopoverTrigger>
            <PopoverContent class="w-auto p-0">
              <RangeCalendar v-model="newGroup.dateRange" initial-focus />
            </PopoverContent>
          </Popover>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Add Members</label>
          <div class="flex gap-2">
            <Input
              v-model="newMemberEmail"
              type="email"
              placeholder="Enter email address"
              class="mt-1"
            />
            <Button
              type="button"
              @click="addMember"
              class="mt-1"
              :disabled="creationStatus.userValidationInProgress"
            >
              <span v-if="creationStatus.userValidationInProgress" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Validating...
              </span>
              <span v-else>Add</span>
            </Button>
          </div>
          <div class="mt-2">
            <div v-for="(member, index) in newGroup.members" :key="index" class="flex items-center gap-2">
              <div class="flex items-center">
                <span class="mr-2">{{ member.email }}</span>
                <span v-if="validatedMembers.some(m => m.email === member.email)" class="text-green-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </span>
                <span v-else class="text-yellow-500 text-xs">(Pending validation)</span>
              </div>
              <Button
                type="button"
                variant="ghost"
                @click="removeMember(index)"
                class="text-red-500 hover:text-red-700"
              >
                Remove
              </Button>
            </div>
          </div>
        </div>
        <!-- Status Visualization -->
        <div class="mt-4 border-t pt-4">
          <h3 class="text-sm font-medium mb-2">Group Creation Status</h3>
          <div class="flex items-center w-full mb-4">
            <div class="flex flex-col items-center w-1/3">
              <div 
                class="w-8 h-8 flex items-center justify-center rounded-full"
                :class="{
                  'bg-green-500 text-white': creationStatus.userValidation,
                  'bg-yellow-500 text-white': creationStatus.userValidationInProgress,
                  'bg-red-500 text-white': creationStatus.userValidationError,
                  'bg-gray-200 text-gray-500': !creationStatus.userValidation && !creationStatus.userValidationInProgress && !creationStatus.userValidationError
                }"
              >
                <svg v-if="creationStatus.userValidation" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="creationStatus.userValidationInProgress" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else-if="creationStatus.userValidationError" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <span v-else>1</span>
              </div>
              <span class="text-xs mt-1 text-center">User Validation</span>
            </div>
            <div class="h-1 w-full bg-green-200">
              <div class="h-1 bg-green-500" :class="{
                'w-full': creationStatus.userValidation,
                'w-1/2': creationStatus.userValidationInProgress,
                'w-0': !creationStatus.userValidation && !creationStatus.userValidationInProgress || !creationStatus.userValidationAttempted
              }"></div>
            </div>
            <div class="flex flex-col items-center w-1/3">
              <div class="w-8 h-8 flex items-center justify-center rounded-full" 
                :class="[
                  creationStatus.groupCreation ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500',
                  isSubmitting ? 'pulse-animation' : ''
                ]">
                <svg v-if="creationStatus.groupCreation" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="isSubmitting" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-else>2</span>
              </div>
              <span class="text-xs mt-1 text-center">Group Creation</span>
            </div>
            <div class="h-1 w-full bg-green-200">
              <div class="h-1 bg-green-500 transition-all duration-300" :class="creationStatus.groupCreation ? 'w-full' : isSubmitting ? 'w-1/2' : 'w-0'"></div>
            </div>
            <div class="flex flex-col items-center w-1/3">
              <div class="w-8 h-8 flex items-center justify-center rounded-full bg-green-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <span class="text-xs mt-1 text-center">Calendar Creation</span>
            </div>
          </div>
          <div v-if="validatedMembers.length > 0" class="text-xs text-gray-700 mb-2">
            <p>Validated users: {{ validatedMembers.map(m => m.email).join(', ') }}</p>
          </div>
          <div v-if="creationStatus.userValidationError" class="text-xs text-red-500 mb-2">
            <p>Validation error: {{ creationStatus.userValidationError }}</p>
          </div>
          <div class="text-xs text-gray-500">
            <p>Note: User validation occurs when you click "Create Group". All members must be validated before a group can be created.</p>
          </div>
        </div>
        <!-- Display testing info -->
        <div class="text-xs text-gray-500 border-t pt-2 mt-2">
          <p>Currently logged in as: {{ userStore.userEmail }}</p>
          <p>User ID: {{ userStore.userId }}</p>
          <p>Start Date: {{ dateFormatter.format(newGroup.dateRange.start.toDate(getLocalTimeZone())) }}</p>
          <p>End Date: {{ dateFormatter.format(newGroup.dateRange.end.toDate(getLocalTimeZone())) }}</p>
        </div>
        <Button
          type="submit"
          class="w-full"
          :disabled="creationStatus.userValidationInProgress || isSubmitting"
        >
          <span v-if="isSubmitting" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Creating Group...
          </span>
          <span v-else-if="creationStatus.userValidationInProgress">Validating User...</span>
          <span v-else>Create Group</span>
        </Button>
      </form>
    </div>

    <!-- Existing Groups -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Your Groups</h2>
        <Button 
          variant="outline" 
          size="sm"
          @click="fetchGroups"
          class="flex items-center gap-1"
          :disabled="isRefreshing"
        >
          <svg v-if="isRefreshing" class="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          <span>{{ isRefreshing ? 'Refreshing...' : 'Refresh' }}</span>
        </Button>
      </div>
      <div v-if="groups.length === 0" class="text-gray-500">
        No groups created yet. Create one above!
      </div>
      <div v-else class="space-y-4">
        <div v-for="group in groups" :key="group.id" 
          :class="[
            'border rounded-lg p-4 transition-all', 
            group.id === newlyCreatedGroupId ? 'border-green-500 shadow-md animate-pulse-light' : ''
          ]">
          <div class="flex justify-between items-start">
            <h3 class="font-semibold">{{ group.name }}</h3>
            <div class="flex gap-2 items-center">
              <div class="text-sm px-2 py-1 rounded" :class="{
                'bg-green-100 text-green-800': group.status === 'completed',
                'bg-yellow-100 text-yellow-800': group.status === 'pending' || group.status === 'partial',
                'bg-red-100 text-red-800': group.status === 'failed'
              }">
                {{ group.status }}
              </div>
              <button 
                @click.stop="confirmDeleteGroup(group)"
                class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-50"
                title="Delete Group"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <p v-if="group.description" class="text-sm text-gray-600 mt-1">{{ group.description }}</p>
          
          <div class="mt-2">
            <h4 class="text-sm font-medium text-gray-700">Members:</h4>
            <ul class="list-disc list-inside">
              <li v-for="member in group.members" :key="member" :class="{ 'font-semibold': member === userStore.userEmail }">
                {{ member }} {{ member === userStore.userEmail ? '(you)' : '' }}
              </li>
            </ul>
          </div>

          <!-- Existing trips section -->
          <div v-if="group.tripsLoading" class="mt-4">
            <p class="text-sm text-gray-500 flex items-center">
              <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading trips...
            </p>
          </div>
          <div v-else-if="group.trips && group.trips.length > 0" class="mt-4">
            <h4 class="text-sm font-medium text-gray-700">Existing Trips:</h4>
            <div class="mt-2 space-y-2">
              <div v-for="trip in group.trips" :key="trip.id" class="bg-gray-50 p-2 rounded flex justify-between items-center">
                <div>
                  <p class="font-medium">{{ trip.city }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(trip.start_date) }} - {{ formatDate(trip.end_date) }}</p>
                </div>
                <Button
                  size="sm"
                  @click="viewTripItinerary(trip.id)"
                  variant="outline"
                >
                  Trip Planning
                </Button>
              </div>
            </div>
          </div>
          <div v-else-if="group.tripsError" class="mt-4">
            <p class="text-sm text-red-500">{{ group.tripsError }}</p>
          </div>
          <div v-else class="mt-4">
            <p class="text-sm text-gray-500">No trips created yet for this group.</p>
            <div class="mt-4">
              <Button
                @click="startTripPlanning(group.id)"
                :disabled="group.status !== 'completed'"
                :class="{ 'opacity-50 cursor-not-allowed': group.status !== 'completed' }"
              >
                Start Trip Planning
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pending Group Invitations -->
    <div class="bg-white rounded-lg shadow p-4 mt-6">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Pending Invitations</h2>
        <Button 
          variant="outline" 
          size="sm"
          @click="fetchPendingInvitations"
          class="flex items-center gap-1"
          :disabled="isRefreshingInvitations"
        >
          <svg v-if="isRefreshingInvitations" class="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          <span>{{ isRefreshingInvitations ? 'Refreshing...' : 'Refresh' }}</span>
        </Button>
      </div>
      <div v-if="pendingInvitations.length === 0" class="text-gray-500">
        No pending invitations.
      </div>
      <div v-else class="space-y-4">
        <div v-for="invitation in pendingInvitations" :key="invitation.id" class="border rounded-lg p-4">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-semibold">{{ invitation.name }}</h3>
              <p class="text-sm text-gray-600 mt-1">Invited by: {{ invitation.invitedBy }}</p>
              <p v-if="invitation.description" class="text-sm text-gray-600 mt-1">{{ invitation.description }}</p>
              
              <div class="mt-2">
                <h4 class="text-sm font-medium text-gray-700">Other Members:</h4>
                <ul class="list-disc list-inside">
                  <li v-for="member in invitation.members" :key="member">
                    {{ member }}
                  </li>
                </ul>
              </div>
              
              <div class="mt-2 text-sm text-gray-600">
                <span>Trip dates: </span>
                <span>{{ formatDate(invitation.startDate) }} - {{ formatDate(invitation.endDate) }}</span>
              </div>
            </div>
            <div class="flex gap-2">
              <Button
                variant="default"
                @click="acceptInvitation(invitation.id)"
                :disabled="isJoiningGroup"
                class="bg-green-600 hover:bg-green-700"
              >
                <span v-if="isJoiningGroup && joiningGroupId === invitation.id" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Joining...
                </span>
                <span v-else>Join Group</span>
              </Button>
              <Button
                variant="outline"
                @click="declineInvitation(invitation.id)"
                :disabled="isDecliningInvitation"
                class="text-red-600 border-red-600 hover:bg-red-50"
              >
                Decline
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium mb-4">Confirm Deletion</h3>
        <p v-if="deleteError" class="mb-4 text-red-500 text-sm bg-red-50 p-2 rounded">
          {{ deleteError }}
        </p>
        <p class="mb-6">Are you sure you want to delete the group "{{ groupToDelete.name }}"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <Button
            variant="outline"
            @click="showDeleteModal = false"
            :disabled="isDeletingGroup"
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            @click="deleteGroup"
            :disabled="isDeletingGroup"
          >
            <span v-if="isDeletingGroup" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Deleting...
            </span>
            <span v-else>Delete</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useUserStore } from '@/stores/user'
import { RangeCalendar } from '@/components/ui/range-calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { DateFormatter, getLocalTimeZone, today, CalendarDate, CalendarDateTime } from '@internationalized/date'
import { CalendarIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const router = useRouter()
const userStore = useUserStore()
const isSubmitting = ref(false)
const showNotification = ref(false)
const lastCreatedGroup = ref({})
const newlyCreatedGroupId = ref(null)
const notificationType = ref('create')
const isRefreshing = ref(false)
const createError = ref('')
const debugInfo = ref({
  show: false,
  data: {}
})

// Pending invitations related
const pendingInvitations = ref([])
const isRefreshingInvitations = ref(false)
const isJoiningGroup = ref(false)
const isDecliningInvitation = ref(false)
const joiningGroupId = ref(null)
const invitationError = ref('')

const dateFormatter = new DateFormatter('en-US', {
  dateStyle: 'long',
})

const notificationMessage = computed(() => {
  if (notificationType.value === 'create') {
    return ` Group "${lastCreatedGroup.value.name}" has been created successfully.`
  } else if (notificationType.value === 'delete') {
    return ` Group "${lastCreatedGroup.value.name}" has been deleted successfully.`
  } else if (notificationType.value === 'join') {
    return ` You have successfully joined "${lastCreatedGroup.value.name}".`
  } else if (notificationType.value === 'decline') {
    return ` You have declined the invitation to "${lastCreatedGroup.value.name}".`
  }
  return ''
})

const creationStatus = ref({
  userValidation: false, // Has not been validated yet
  userValidationInProgress: false,
  userValidationError: null,
  userValidationAttempted: false, // Track if validation has been attempted
  groupCreation: false,
  calendarCreation: true
})

const newGroup = ref({
  name: '',
  members: [],
  createdBy: computed(() => userStore.userId),
  dateRange: { 
    start: today(getLocalTimeZone()), 
    end: today(getLocalTimeZone()).add({ months: 1 })
  }
})
const newMemberEmail = ref('')
const groups = ref([])
const validatedMembers = ref([])

const showDeleteModal = ref(false)
const groupToDelete = ref({})
const isDeletingGroup = ref(false)
const deleteError = ref('')

// Check if the creator is validated
onMounted(async () => {
  if (userStore.isAuthenticated) {
    fetchGroups()
    fetchPendingInvitations()
  } else {
    // If not authenticated, redirect to login
    router.push('/login')
  }
})

const validateCurrentUser = async () => {
  try {
    creationStatus.value.userValidationInProgress = true
    creationStatus.value.userValidationError = null
    creationStatus.value.userValidationAttempted = true
    
    // Reset validation status to pending
    creationStatus.value.userValidation = false
    
    // Check if current user exists
    const response = await fetch(`http://localhost:5001/api/users/${userStore.userId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      // User exists, set validation as successful
      creationStatus.value.userValidation = true
      // Add current user to validated members
      validatedMembers.value = [{
        email: userStore.userEmail,
        userId: userStore.userId
      }]
      return true
    } else {
      creationStatus.value.userValidation = false
      creationStatus.value.userValidationError = 'Current user validation failed'
      return false
    }
  } catch (error) {
    console.error('Error validating user:', error)
    creationStatus.value.userValidation = false
    creationStatus.value.userValidationError = error.message
    return false
  } finally {
    creationStatus.value.userValidationInProgress = false
  }
}

const verifyEmail = async (email) => {
  try {
    creationStatus.value.userValidationInProgress = true
    
    const response = await fetch(`http://localhost:5003/api/verify-user?email=${encodeURIComponent(email)}`, {
      headers: {
        'X-User-ID': userStore.userId.toString()
      }
    })
    
    if (response.ok) {
      // Check Content-Type to determine if we should parse JSON
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.includes('application/json')) {
        try {
          const result = await response.json();
          
          if (result.exists) {
            // Add to validated members list
            if (!validatedMembers.value.some(m => m.email === email)) {
              validatedMembers.value.push({ email });
            }
            
            // Return the user information including ID if available
            return {
              exists: true,
              userId: result.userId || null,
              email: email
            };
          }
          
          return { exists: false };
        } catch (jsonError) {
          console.error('Error parsing JSON from verify-user endpoint:', jsonError);
          // If parsing failed but response was OK, assume user exists
          if (!validatedMembers.value.some(m => m.email === email)) {
            validatedMembers.value.push({ email });
          }
          return {
            exists: true,
            userId: null,
            email: email,
            note: 'User exists but ID could not be determined'
          };
        }
      } else {
        // If response is OK but not JSON, assume user exists
        if (!validatedMembers.value.some(m => m.email === email)) {
          validatedMembers.value.push({ email });
        }
        return {
          exists: true,
          userId: null,
          email: email,
          note: 'User exists but ID could not be determined'
        };
      }
    }
    
    return { exists: false };
  } catch (error) {
    console.error('Error verifying email:', error);
    return { exists: false, error: error.message };
  } finally {
    creationStatus.value.userValidationInProgress = false;
  }
}

const addMember = async () => {
  if (!newMemberEmail.value || newGroup.value.members.some(m => m.email === newMemberEmail.value)) {
    return
  }
  
  if (newMemberEmail.value === userStore.userEmail) {
    alert("You can't add yourself as a member. You're automatically included as the creator.")
    newMemberEmail.value = ''
    return
  }
  
  // Verify if user exists
  const userExists = await verifyEmail(newMemberEmail.value)
  if (userExists.exists) {
    newGroup.value.members.push({
      email: newMemberEmail.value,
      userId: userExists.userId
    })
    newMemberEmail.value = ''
  } else {
    alert('User with this email does not exist in the system')
  }
}

const removeMember = (index) => {
  const memberToRemove = newGroup.value.members[index]
  newGroup.value.members.splice(index, 1)
  
  // Remove from validated members if present
  const validatedIndex = validatedMembers.value.findIndex(m => m.email === memberToRemove.email)
  if (validatedIndex > -1) {
    validatedMembers.value.splice(validatedIndex, 1)
  }
}

const createGroup = async () => {
  try {
    isSubmitting.value = true
    createError.value = ''

    // First, validate the current user
    const isUserValid = await validateCurrentUser()
    if (!isUserValid) {
      isSubmitting.value = false
      return
    }
    
    // Update group creation status
    setTimeout(() => {
      creationStatus.value.groupCreation = true
    }, 1000) // Simulate a delay before completing
    
    // Convert CalendarDate objects to ISO strings for API
    const startDate = newGroup.value.dateRange.start.toDate(getLocalTimeZone());
    const endDate = newGroup.value.dateRange.end.toDate(getLocalTimeZone());
    
    // Format ISO strings without milliseconds
    const startDateISO = startDate.toISOString().split('.')[0] + 'Z';
    const endDateISO = endDate.toISOString().split('.')[0] + 'Z';
    
    const payload = {
      name: newGroup.value.name,
      users: [userStore.userId, ...newGroup.value.members.map(m => m.userId || 0)], // Include current user ID and member IDs
      createdBy: userStore.userId,
      startDateRange: startDateISO,
      endDateRange: endDateISO,
      description: 'Created for testing purposes'
    }

    // Store payload in debug info
    debugInfo.value.data = {
      request: {
        url: 'http://localhost:5003/api/groups',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userStore.userId.toString()
        },
        payload
      }
    }

    const response = await fetch('http://localhost:5003/api/groups', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userStore.userId.toString()
      },
      body: JSON.stringify(payload)
    })
    
    // Add response status to debug info
    debugInfo.value.data.response = {
      status: response.status,
      statusText: response.statusText
    }

    // Check if response has content before parsing JSON
    let responseData;
    try {
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        // If not JSON, get text content
        const textContent = await response.text();
        responseData = { message: textContent || 'No content returned' };
      }
    } catch (error) {
      console.error('Error parsing response:', error);
      responseData = { error: 'Failed to parse response data', details: error.message };
    }
    
    // Add response data to debug info
    debugInfo.value.data.response.data = responseData
    debugInfo.value.show = true
    
    if (response.ok) {
      const group = responseData
      
      // Refresh the groups list instead of manually adding
      await fetchGroups()
      
      // Store the new group for notification
      lastCreatedGroup.value = {
        name: group.name,
        id: group.id || group.group_id
      }
      
      // Set notification type
      notificationType.value = 'create'
      
      // Set the newly created group ID to highlight it
      newlyCreatedGroupId.value = group.id || group.group_id
      
      // Show success notification
      showNotification.value = true
      
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 5000)
      
      // Auto-remove highlight after 3 seconds
      setTimeout(() => {
        newlyCreatedGroupId.value = null
      }, 3000)
      
      // Reset form and status after successful creation
      newGroup.value = {
        name: '',
        members: [],
        createdBy: userStore.userId,
        dateRange: { 
          start: today(getLocalTimeZone()), 
          end: today(getLocalTimeZone()).add({ months: 1 })
        }
      }
      validatedMembers.value = [{
        email: userStore.userEmail,
        userId: userStore.userId
      }]
      
      // Keep success status visible for a moment before resetting
      setTimeout(() => {
        isSubmitting.value = false
        setTimeout(() => {
          creationStatus.value.userValidation = false
          creationStatus.value.userValidationAttempted = false
          creationStatus.value.userValidationInProgress = false
          creationStatus.value.groupCreation = false
        }, 1500)
      }, 500)
      console.log('Group created successfully:', group)
    } else {
      isSubmitting.value = false
      creationStatus.value.groupCreation = false
      createError.value = responseData.error || 'Failed to create group'
      console.error('Failed to create group:', responseData)
    }
  } catch (error) {
    isSubmitting.value = false
    creationStatus.value.groupCreation = false
    createError.value = error.message || 'An unexpected error occurred'
    debugInfo.value.data.error = {
      message: error.message,
      stack: error.stack
    }
    debugInfo.value.show = true
    console.error('Error creating group:', error)
  }
}

const fetchGroups = async () => {
  try {
    if (!userStore.isAuthenticated) {
      console.error('User not authenticated')
      return
    }

    isRefreshing.value = true
    
    const response = await fetch(`http://localhost:5003/api/groups/user/${userStore.userId}`, {
      headers: {
        'X-User-ID': userStore.userId.toString(),
        'X-User-Email': userStore.userEmail || ''
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Process each group
      const groupsWithEmailPromises = data.map(async (item) => {
        // Initialize members as empty array if not present
        const userIds = item.UserIds || [];
        
        // Fetch email for each user ID
        const memberEmailPromises = userIds.map(async (userId) => {
          try {
            const userResponse = await fetch(`http://localhost:5001/api/users/${userId}`);
            if (userResponse.ok) {
              const userData = await userResponse.json();
              return userData.email || `User ${userId}`;
            } else {
              console.error(`Failed to fetch user data for ID ${userId}`);
              return `User ${userId}`;
            }
          } catch (error) {
            console.error(`Error fetching user data for ID ${userId}:`, error);
            return `User ${userId}`;
          }
        });
        
        // Wait for all user email fetches to complete
        const memberEmails = await Promise.all(memberEmailPromises);
        
        // Find existing group to preserve trip data
        const existingGroup = groups.value.find(g => g.id === (item.group_id || item.Id));
        
        const groupData = {
          id: item.group_id || item.Id,
          name: item.Name,
          memberIds: item.UserIds || [],
          members: memberEmails,
          description: item.Description,
          status: 'completed',
          trips: [],
          tripsLoaded: false,
          tripsLoading: true,
          tripsError: null
        };
        
        // Fetch trips for each group
        await fetchTripsForGroup(groupData);
        
        return groupData;
      });
      
      // Wait for all groups to be processed
      groups.value = await Promise.all(groupsWithEmailPromises);
    } else {
      const errorText = await response.text()
      console.error('Failed to fetch groups:', errorText)
      createError.value = `Failed to fetch groups: ${errorText}`
    }
  } catch (error) {
    console.error('Error fetching groups:', error)
    createError.value = `Error fetching groups: ${error.message}`
  } finally {
    isRefreshing.value = false
  }
}

const fetchTripsForGroup = async (group) => {
  try {
    if (!group.id) {
      console.error('Group ID not defined')
      return
    }
    
    group.tripsLoading = true
    group.tripsError = null
    group.tripsLoaded = false
    
    const response = await fetch(`http://localhost:5005/api/groups/${group.id}/trips`, {
      headers: {
        'X-User-ID': userStore.userId.toString()
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      group.trips = Array.isArray(data) ? data : []
      group.tripsLoaded = true
      group.tripsLoading = false
    } else if (response.status === 404) {
      // No trips found is a normal condition, not an error
      group.trips = []
      group.tripsLoaded = true
      group.tripsLoading = false
    } else {
      const errorText = await response.text()
      console.error(`Failed to fetch trips for group ${group.id}:`, errorText)
      group.tripsError = `Error loading trips: ${errorText}`
      group.tripsLoaded = false
      group.tripsLoading = false
    }
  } catch (error) {
    console.error(`Error fetching trips for group ${group.id}:`, error)
    group.tripsError = `Error: ${error.message}`
    group.tripsLoaded = false
    group.tripsLoading = false
  }
}

const viewTripItinerary = (tripId) => {
  router.push({
    name: 'trip-planning',
    params: { tripId }
  })
}

const startTripPlanning = (groupId) => {
  router.push({
    name: 'trip-ideation',
    params: { groupId }
  })
}

const confirmDeleteGroup = (group) => {
  groupToDelete.value = group
  deleteError.value = ''
  showDeleteModal.value = true
}

const deleteGroup = async () => {
  try {
    isDeletingGroup.value = true
    deleteError.value = ''
    console.log('Deleting group:', groupToDelete.value)
    const response = await fetch(`http://localhost:5003/api/groups/${groupToDelete.value.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userStore.userId.toString()
      }
    })
    
    if (response.ok) {
      // Remove the group from the list
      groups.value = groups.value.filter(g => g.id !== groupToDelete.value.id)
      
      // Close modal and show success notification
      showDeleteModal.value = false
      isDeletingGroup.value = false
      
      // Update the notification to show delete success
      lastCreatedGroup.value = {
        name: groupToDelete.value.name
      }
      notificationType.value = 'delete'
      showNotification.value = true
      
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 5000)
      
      console.log('Group deleted successfully')
    } else {
      isDeletingGroup.value = false
      const errorText = await response.text()
      deleteError.value = `Failed to delete group: ${errorText || 'Unknown error'}`
      console.error('Failed to delete group:', errorText)
    }
  } catch (error) {
    isDeletingGroup.value = false
    deleteError.value = `Error: ${error.message || 'Unknown error'}`
    console.error('Error deleting group:', error)
  }
}

// Add function to return to dashboard
const returnToDashboard = () => {
  router.push('/dashboard')
}

// Format dates for display in invitations
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return dateFormatter.format(date)
}

// Fetch pending invitations
const fetchPendingInvitations = async () => {
  try {
    if (!userStore.isAuthenticated) {
      console.error('User not authenticated')
      return
    }

    isRefreshingInvitations.value = true
    
    // Fetch invitations where the user has been invited but not yet joined
    const response = await fetch(`http://localhost:5003/api/groups/invited/${userStore.userId}`, {
      headers: {  
        'X-User-ID': userStore.userId.toString(),
        'X-User-Email': userStore.userEmail || ''
      }
    })
    
    // For debugging
    debugInfo.value.data.invitations = {
      url: `http://localhost:5003/api/groups/invited/${userStore.userId}`,
      headers: {
        'X-User-ID': userStore.userId.toString(),
        'X-User-Email': userStore.userEmail || ''
      },
      status: response.status,
      statusText: response.statusText
    }
    
    if (response.ok) {
      try {
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          debugInfo.value.data.invitations.data = data;
          
          pendingInvitations.value = data.map(item => ({
            id: item.group_id || item.id,
            name: item.name || '',
            invitedBy: item.created_by_email || `Invited by ${item.invitedBy}`,
            description: item.description || '',
            startDate: item.startDate || '',
            endDate: item.endDate || '',
            members: item.members || []
          }));
        }
      } catch (error) {
        console.error('Error parsing invitations:', error);
      }
    } else {
      console.error('Error fetching pending invitations:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching pending invitations:', error);
  } finally {
    isRefreshingInvitations.value = false;
  }
}

const acceptInvitation = async (groupId) => {
  try {
    isJoiningGroup.value = true
    joiningGroupId.value = groupId
    invitationError.value = ''
    
    const invitation = pendingInvitations.value.find(i => i.id === groupId)
    if (!invitation) {
      console.error('Invitation not found')
      return
    }
    
    const response = await fetch(`http://localhost:5003/api/groups/${groupId}/join`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userStore.userId.toString(),
        'X-User-Email': userStore.userEmail || ''
      },
      body: JSON.stringify({
        user_id: userStore.userId
      })
    })
    
    if (response.ok) {
      // Remove from pending invitations
      pendingInvitations.value = pendingInvitations.value.filter(i => i.id !== groupId)
      
      // Update the notification
      lastCreatedGroup.value = {
        name: invitation.name
      }
      notificationType.value = 'join'
      showNotification.value = true
      
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 5000)
      
      // Refresh the groups list to show the new group
      await fetchGroups()
      
      console.log('Successfully joined group')
    } else {
      const errorText = await response.text()
      invitationError.value = `Failed to join group: ${errorText}`
      console.error('Failed to join group:', errorText)
    }
  } catch (error) {
    console.error('Error joining group:', error)
    invitationError.value = `Error joining group: ${error.message}`
  } finally {
    isJoiningGroup.value = false
    joiningGroupId.value = null
  }
}

const declineInvitation = async (groupId) => {
  try {
    isDecliningInvitation.value = true
    invitationError.value = ''
    
    const invitation = pendingInvitations.value.find(i => i.id === groupId)
    if (!invitation) {
      console.error('Invitation not found')
      return
    }
    
    // Remove from pending invitations (client-side only)
    pendingInvitations.value = pendingInvitations.value.filter(i => i.id !== groupId)
    
    // Update the notification
    lastCreatedGroup.value = {
      name: invitation.name
    }
    notificationType.value = 'decline'
    showNotification.value = true
    
    // Auto-dismiss notification after 5 seconds
    setTimeout(() => {
      showNotification.value = false
    }, 5000)
    
    console.log('Declined invitation')
  } catch (error) {
    console.error('Error declining invitation:', error)
    invitationError.value = `Error declining invitation: ${error.message}`
  } finally {
    isDecliningInvitation.value = false
  }
}
</script>

<style scoped>
/* Add your styles here */
</style>

<script>
export default {
  // Add any necessary component options here
}
</script>

<style>
/* Add any necessary styles here */
</style>