#pragma once

#include "Game/CPhysicsActor.h"

class CActor;
class CFSMProperties;
class CRenderManager;
class CStateManager;
class CTransform4f;

namespace NImposter
{
    enum ESortLayer
    {

    };
}

class CGameCharacter : public CPhysicsActor
{
public:
    enum ESortFlags
    {

    };

    ~CGameCharacter() override;

    bool TypesMatch(int) const override;
    void Think(f32, CStateManager&) override;
    void AcceptScriptMsg(CStateManager&, const CScriptMsg&) override;
    void* HealthInfo() override;
    void GetDamageVulnerability() const override;
    void Touch(CStateManager&, CActor&) override;
    void PreRenderInViewport(CRenderManager&) override;
    void PreRenderForWholeScene(CRenderManager&) override;
    virtual void AddToSpecialSort(CRenderManager&, ESortFlags) const;
    virtual void CanRenderSortWith(const CStateManager&, const CActor&, NImposter::ESortLayer, NImposter::ESortLayer) const;
    virtual void GetRenderSortLayer(const CStateManager&) const;
    virtual void DamageVulnerability();
    virtual void UnkCC();
    virtual void UnkD0();
    virtual void UnkD4();
    virtual void SetupAIStateMachine(CStateManager&);
    virtual void SetupAnimStateMachine(CStateManager&);
    virtual void SyncToCurrentMovementSpeed(CStateManager&, const CFSMProperties&, f32);
    virtual void SetSplinePathId(CStateManager&, TUniqueId);
    virtual void GetTransformOnSpline(const CStateManager&)const;
    virtual void UnkEC();
    virtual void UnkF0();
    virtual void NotifyThrownObjectKill(CStateManager&, const TUniqueId&, const CTransform4f&);
    virtual void NotifyThrownObjectFinished(CStateManager&, const TUniqueId&);
    virtual void AfterMovePlayers(CStateManager&, f32);
};
