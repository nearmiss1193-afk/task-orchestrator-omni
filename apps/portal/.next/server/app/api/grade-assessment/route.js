"use strict";(()=>{var e={};e.id=2597,e.ids=[2597],e.modules={20399:e=>{e.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},30517:e=>{e.exports=require("next/dist/compiled/next-server/app-route.runtime.prod.js")},38465:(e,t,s)=>{s.r(t),s.d(t,{originalPathname:()=>d,patchFetch:()=>g,requestAsyncStorage:()=>p,routeModule:()=>u,serverHooks:()=>m,staticGenerationAsyncStorage:()=>l});var r={};s.r(r),s.d(r,{POST:()=>c});var a=s(49303),o=s(88716),n=s(60670),i=s(87070);async function c(e){try{let{industry:t,companySize:s,primaryChallenge:r,currentCRM:a,email:o}=await e.json();console.log(`[LEAD CAPTURED] Assessment completed for ${o} in ${t}`);let n=`You are an elite AI Automation Architect. A local service business owner just took our "AI Readiness Assessment".
        
        Business Data:
        - Industry: ${t}
        - Primary Bottleneck: ${r}
        - Current CRM: ${a}
        
        Task:
        1. Give them an "AI Readiness Score" from 1-100 (Be realistic, usually 30-70 for local businesses).
        2. Write a 2-sentence analysis of their current operational bottleneck.
        3. Provide exactly 3 bullet points of specific AI workflows we (AI Service Co) should install for them.
        
        Return ONLY valid JSON in this exact format, with no markdown formatting or backticks:
        {
            "score": 45,
            "analysis": "Your business is...",
            "recommendations": ["Workflow 1", "Workflow 2", "Workflow 3"]
        }`,c=process.env.GEMINI_API_KEY||process.env.GOOGLE_API_KEY;if(!c)return i.NextResponse.json({score:42,analysis:`Your ${t} business is losing significant revenue to manual operations. Your current setup relying on ${a||"manual entry"} is creating a severe bottleneck with ${r.toLowerCase()}.`,recommendations:["Deploy an AI Voice Receptionist to answer 24/7","Install our Speed-to-Lead SMS sequence","Activate an autonomous Database Reactivation campaign"]});let u=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${c}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({contents:[{parts:[{text:n}]}],generationConfig:{temperature:.2,response_mime_type:"application/json"}})}),p=(await u.json()).candidates[0].content.parts[0].text.replace(/```json/g,"").replace(/```/g,"").trim(),l=JSON.parse(p);return i.NextResponse.json(l)}catch(e){return console.error("API Route Error:",e),i.NextResponse.json({error:"Failed to process assessment"},{status:500})}}let u=new a.AppRouteRouteModule({definition:{kind:o.x.APP_ROUTE,page:"/api/grade-assessment/route",pathname:"/api/grade-assessment",filename:"route",bundlePath:"app/api/grade-assessment/route"},resolvedPagePath:"C:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\apps\\portal\\src\\app\\api\\grade-assessment\\route.ts",nextConfigOutput:"",userland:r}),{requestAsyncStorage:p,staticGenerationAsyncStorage:l,serverHooks:m}=u,d="/api/grade-assessment/route";function g(){return(0,n.patchFetch)({serverHooks:m,staticGenerationAsyncStorage:l})}}};var t=require("../../../webpack-runtime.js");t.C(e);var s=e=>t(t.s=e),r=t.X(0,[8948,5972],()=>s(38465));module.exports=r})();