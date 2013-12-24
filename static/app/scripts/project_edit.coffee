console.log "project_edit.js"

TEMPLATE_TYPE_MAP=[
	{id:'banner_320x50',text:'banner_320x50'},
	{id:'banner_300x250',text:'banner_300x250'},
	{id:'banner_728x90',text:'banner_728x90'},
	{id:'interstitial',text:'interstitial'}
]

DEFAULT_RICHMEDIA_INFO='{"cid":"test-cid-1218","crid":"dev_crid","partner_id":"dev_partner_id","idfa":"dev_idfa","idfasha1":"feeba08fb17a6f16b9371c4645237fcca0f31d57","idfamd5":"728b0eb2d67265641024f14baf702ccf","androidid":"dev_androidid","androididsha1":"3d7f00b9acc51b62780eac297faff853fb871e42","androididmd5":"ae593350584ce7fa80ce580d6c8269b2","bidobjid":"dev_bidobjid","reqid":"dev_reqid"}'

DEFAULT_BEACON1='<img src="http://######/transparent.gif">'

DEFAULT_CLICK_THROUGH_URL='http://www.appier.com'

project=
	save:(data,options)->
		options?={}
		$.ajax(
			url:'/project/edit'
			type:'post'
			data:data
			success:(response)->
				console.dir(response)
				if typeof options.success=='function' 
					options.success.apply(this,arguments)
		)
	get_one:(id,options)->
		options?={}
		url='/project/read/'+id;
		$.getJSON url,(response)->
			if typeof options.success=='function' 
				options.success.apply(this,arguments)
#console.dir top.location
#query=URI.parseQuery()
init=()->
	console.log("init")
	$(".btn-submit").attr('disabled','disabled')

	query=URI(console.log top.location.href).search()
	query=URI.parseQuery(query or "")
	current_project=null
	if !query.project_id
		alert('project is not ready')

	else if query.project_id
		project.get_one query.project_id,
			success:(response)->
				console.dir(response)
				if response.code==200
					current_project=response.result
					init_ui(current_project)
				else
					alert('project is not exist')
#end of init


init_ui=(current_project)->
	console.dir current_project
	$("input[name='project_id']").val(current_project.project_id)
	$("input[name='name']").val(current_project.name)
	val=if current_project.public	then "true" else "false"
	$("input[name='public'][value='#{val}']").prop('checked',true)
	$("input[name='template_type']").val(current_project.template_type).select2 data:TEMPLATE_TYPE_MAP
	$("input[name='url']").val(current_project.url)
	$("input[name='assets_url']").val(current_project.assets_url)
	$("input[name='click_through_url']").val(current_project.click_through_url or DEFAULT_CLICK_THROUGH_URL)
	$("input[name='beacon1']").val(current_project.beacon1 or DEFAULT_BEACON1)
	$("textarea[name='richmedia_info']").val(current_project.richmedia_info or DEFAULT_RICHMEDIA_INFO)
	$("textarea[name='inject_snippet']").val(current_project.inject_snippet)

	$(".btn-mraid-preview").attr('href','/project/preview/'+current_project.project_id)


	$(".btn-submit").removeAttr('disabled')
	$(".btn-submit").click ()->
		data=
			project_id:$("input[name='project_id']").val() or null
			name:$("input[name='name']").val()
			public:if $("input[name='public']:checked").val()=="true" then true else false
			template_type:$("input[name='template_type']").select2 'val'
			url:$("input[name='url']").val()
			assets_url:$("input[name='assets_url']").val()
			click_through_url:$("input[name='click_through_url']").val()
			beacon1:$("input[name='beacon1']").val()
			richmedia_info:$("textarea[name='richmedia_info']").val()
			inject_snippet:$("textarea[name='inject_snippet']").val()
		console.log("post data")
		console.dir(data)
		options=
			success:(response)->
				console.log "SUCCESS"
				alert("save complete")
			error:(response)->
				console.log "ERROR"
		project.save(data,options)	
		
#end of init_ui==============
init()
