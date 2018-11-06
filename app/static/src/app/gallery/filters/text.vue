<template>
	<div class="input-group right-align">
		<div class="form-field">
			<input v-model="search" type="text" placeholder="Filter by name or text..." :disabled="isDisabled">
		</div>
		<button @click="clearSearch" :disabled="!search || isDisabled" class="btn" title="Clear Search"><i class="fa fa-times"></i></button>
	</div>
</template>

<script>
	import {debounce} from 'lodash'

	export default {
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			},
			search: {
				get () {
					return this.$store.state.options.search
				},
				set: debounce(function (value) {
					let search = value || null
					this.$store.commit('setSearch', search)
					this.$store.dispatch('filterCards')
				}, 750)
			}
		},
		methods: {
			clearSearch () {
				this.search = null
			}
		}
	}
</script>

