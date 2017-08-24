<template>
	<div id="editor-gallery">
		<p>Card gallery WIP: {{ count }}</p>
		<p></p>
	</div>
</template>

<script>
	export default {
		computed: {
			count () {
		    	return this.$store.state.count
		    }
		}
	}
</script>
