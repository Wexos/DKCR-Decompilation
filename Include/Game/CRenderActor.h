#pragma once

#include "Game/CActor.h"

class CAdvancementDeltas;
class CAnimUserNotify;
class CRenderManager;
class CStateManager;
class IAnimParticleManager;

namespace NAnim
{
    enum EEventState
    {

    };
}

class CRenderActor : public CActor
{
public:
    ~CRenderActor() override;

    bool TypesMatch(int) const override;
    void AcceptScriptMsg(CStateManager&, const CScriptMsg&) override;
    void SetActive(CStateManager&, bool) override;
    void SetTransformDirty() override;
    void GetDetailedTouchBounds() const override;
    void DetailedTouchBounds() override;
    virtual void GetShadowHitResponse(const CStateManager&) const;
    virtual void PreRenderInViewport(CRenderManager&);
    virtual void PreRenderForWholeScene(CRenderManager&);
    virtual void RenderUnsortedAndAddSorted(const CRenderManager&) const;
    virtual void RenderUnsortedModelData(const CRenderManager&) const;
    virtual void RenderSorted(const CRenderManager&) const;
    virtual void RenderParticlesSortedWithActorFirst(const IAnimParticleManager*) const;
    virtual void RenderParticlesSortedWithActorLast(const IAnimParticleManager*) const;
    virtual void DoUserAnimEvent(CStateManager&, const CAnimUserNotify&, NAnim::EEventState, f32);
    virtual void CanRenderShadow(const CStateManager&) const;
    virtual void OnAnimationAdvancement(const CAdvancementDeltas&);
};
